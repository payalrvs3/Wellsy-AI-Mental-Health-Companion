"""Analytics over mood check-ins. Timestamps are stored in UTC and converted to the user's timezone here."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pandas as pd

from core.content import ASSESSMENTS

MOOD_COLUMNS = ["id", "score", "emotions", "activities", "sleep_hours", "note", "logged_at"]
WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def valid_zone(name):
    """`name` if this system knows the timezone, else UTC. Browsers can report legacy names like Asia/Calcutta."""
    try:
        ZoneInfo(name)
    except (KeyError, ValueError, OSError):
        return "UTC"
    return name


def today(tz="UTC") -> date:
    return datetime.now(ZoneInfo(tz)).date()


def local(timestamp, tz="UTC", fmt="%d %b, %I:%M %p"):
    return pd.Timestamp(timestamp, tz="UTC").tz_convert(tz).strftime(fmt)


def mood_frame(rows, tz="UTC"):
    df = pd.DataFrame(rows, columns=MOOD_COLUMNS)
    at = pd.to_datetime(df["logged_at"], utc=True).dt.tz_convert(tz).dt.tz_localize(None)
    return df.assign(at=at, day=at.dt.normalize())


def window(df, end: date, days):
    """Rows whose local day falls in the `days` days ending on `end` (inclusive)."""
    end = pd.Timestamp(end)
    return df[(df["day"] > end - pd.Timedelta(days=days)) & (df["day"] <= end)]


def daily(df):
    return df.groupby("day", as_index=False).agg(mood=("score", "mean"), n=("score", "size"))


def streak(df, end: date):
    """Consecutive days with a check-in, ending today (or yesterday if today has none yet)."""
    days = set(df["day"].dt.date)
    day = end if end in days else end - timedelta(days=1)
    count = 0
    while day in days:
        count += 1
        day -= timedelta(days=1)
    return count


def _split(df, column):
    """One row per comma-separated value in `column`."""
    items = df.assign(item=df[column].str.split(",")).explode("item")
    items["item"] = items["item"].str.strip()
    return items[items["item"] != ""]


def tally(df, column, top=8):
    return _split(df, column)["item"].value_counts().head(top)


def weekday_avg(df):
    return df.groupby(df["at"].dt.strftime("%a"))["score"].mean().reindex(WEEKDAYS).dropna()


def activity_lift(df, min_entries=3):
    """Average mood with each activity minus the overall average."""
    grouped = _split(df, "activities").groupby("item")["score"].agg(["mean", "size"])
    return (grouped[grouped["size"] >= min_entries]["mean"] - df["score"].mean()).sort_values()


def mood_summary(df, end: date, days=7):
    """One-line summary of recent check-ins, used as optional context for the AI."""
    recent = window(df, end, days)
    if recent.empty:
        return ""
    feelings = ", ".join(tally(recent, "emotions", 3).index)
    text = f"last {days} days: {len(recent)} check-ins, average mood {recent['score'].mean():.1f}/5"
    return text + (f", most common feelings: {feelings}" if feelings else "")


def checkin_summary(rows):
    """Most recent score and severity band per questionnaire kind, used as optional context for the AI."""
    latest = {}
    for row in sorted(rows, key=lambda r: r["created_at"]):
        latest[row["kind"]] = row
    parts = [f"{kind} {row['score']} ({severity(ASSESSMENTS[kind], row['score'])[0]})" for kind, row in latest.items()]
    return ", ".join(parts)


def journal_summary(rows, days=7):
    """Entry count and tags from the last `days` days, used as optional context for the AI."""
    cutoff = (datetime.now(UTC) - timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")
    recent = [r for r in rows if r["created_at"] > cutoff]
    if not recent:
        return ""
    tags = dict.fromkeys(t.strip() for r in recent for t in r["tags"].split(",") if t.strip())
    themes = f", themes: {', '.join(list(tags)[:5])}" if tags else ""
    return f"{len(recent)} entries in the last {days} days{themes}"


def context_summary(moods_df, assessment_rows, journal_rows, end: date, days=7):
    """Combined mood, check-in and journal summary, used as optional context for the AI."""
    parts = []
    if mood := mood_summary(moods_df, end, days):
        parts.append(f"mood — {mood}")
    if checkins := checkin_summary(assessment_rows):
        parts.append(f"check-ins — {checkins}")
    if journal := journal_summary(journal_rows, days):
        parts.append(f"journal — {journal}")
    return "; ".join(parts)


def summary_markdown(name, df, assessments, tz="UTC"):
    """A plain-language report the user can share with a doctor or counsellor."""
    lines = [f"# Wellsy summary for {name}", f"Generated {today(tz):%d %b %Y}", ""]
    if not df.empty:
        first, last = df["day"].min().strftime("%d %b %Y"), df["day"].max().strftime("%d %b %Y")
        lines += [
            "## Mood check-ins",
            f"- {len(df)} check-ins between {first} and {last}",
            f"- Average mood: {df['score'].mean():.1f} / 5",
            f"- Most common feelings: {', '.join(tally(df, 'emotions', 5).index) or 'none recorded'}",
        ]
        lift = activity_lift(df)
        if not lift.empty:
            lines.append(
                f"- Activities linked with better mood: {', '.join(lift[lift > 0].index[::-1][:3]) or 'none yet'}"
            )
    if assessments:
        lines += ["", "## Screening scores (not a diagnosis)"]
        lines += [f"- {local(a['created_at'], tz, '%d %b %Y')}: {a['kind']} = {a['score']}" for a in assessments]
    return "\n".join(lines)


def severity(test, score):
    """(label, guidance) for the band that contains `score`."""
    return next((label, advice) for cap, label, advice in test["bands"] if score <= cap)
