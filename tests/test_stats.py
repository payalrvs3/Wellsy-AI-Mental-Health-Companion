from datetime import UTC, date, datetime, timedelta

import pytest

from core import stats
from core.content import ASSESSMENTS


def entry(timestamp, score, emotions="", activities=""):
    return {
        "id": 1, "score": score, "emotions": emotions, "activities": activities,
        "sleep_hours": None, "note": "", "logged_at": timestamp,
    }  # fmt: skip


def frame(*entries, tz="UTC"):
    return stats.mood_frame(list(entries), tz)


def days_ago(n):
    return (datetime.now(UTC) - timedelta(days=n)).strftime("%Y-%m-%d %H:%M:%S")


SAMPLE = [
    entry(f"2026-09-{day:02d} 09:00:00", score, emotions, activities)
    for day, score, emotions, activities in [
        (1, 5, "Calm,Happy", "Exercise"),
        (2, 5, "Calm", "Exercise"),
        (3, 4, "Happy", "Exercise,Friends"),
        (4, 2, "Sad", "Screen time"),
        (5, 1, "Sad,Tired", "Screen time"),
        (6, 2, "Tired", "Screen time"),
        (7, 3, "Calm", "Rest"),
    ]
]


def test_timestamps_become_the_local_day():
    df = frame(entry("2026-09-20 20:00:00", 3), tz="Asia/Kolkata")
    assert df["day"].iloc[0].date() == date(2026, 9, 21)
    assert stats.local("2026-09-20 20:00:00", "Asia/Kolkata", "%d %b %H:%M") == "21 Sep 01:30"


def test_unknown_timezones_fall_back_to_utc():
    assert stats.valid_zone("Asia/Kolkata") == "Asia/Kolkata"
    assert stats.valid_zone("Nowhere/Land") == "UTC" and stats.valid_zone("") == "UTC"


def test_empty_data_is_handled():
    df = frame()
    assert df.empty and stats.streak(df, date(2026, 9, 21)) == 0
    assert stats.tally(df, "emotions").empty and stats.mood_summary(df, date(2026, 9, 21)) == ""


def test_streak_counts_back_from_today_or_yesterday():
    df = frame(*(entry(f"2026-09-{d} 08:00:00", 3) for d in (21, 20, 19, 17)))
    assert stats.streak(df, date(2026, 9, 21)) == 3
    assert stats.streak(df, date(2026, 9, 22)) == 3
    assert stats.streak(df, date(2026, 9, 25)) == 0


def test_window_includes_today_and_excludes_the_start_day():
    df = frame(entry("2026-09-14 10:00:00", 1), entry("2026-09-15 10:00:00", 2), entry("2026-09-21 10:00:00", 3))
    assert list(stats.window(df, date(2026, 9, 21), 7)["score"]) == [2, 3]


def test_tally_weekday_and_activity_lift():
    df = frame(*SAMPLE)
    assert stats.tally(df, "emotions").to_dict() == {"Calm": 3, "Happy": 2, "Sad": 2, "Tired": 2}
    weekdays = stats.weekday_avg(df)
    assert list(weekdays.index) == stats.WEEKDAYS and weekdays["Mon"] == 3
    lift = stats.activity_lift(df)
    assert list(lift.index) == ["Screen time", "Exercise"] and lift["Exercise"] > 0 > lift["Screen time"]


def test_mood_summary_is_a_single_line_for_the_ai():
    text = stats.mood_summary(frame(*SAMPLE), date(2026, 9, 7))
    assert "7 check-ins" in text and "3.1/5" in text and "Calm" in text
    assert stats.mood_summary(frame(*SAMPLE), date(2026, 10, 30)) == ""


@pytest.mark.parametrize(
    ("kind", "score", "label"),
    [("PHQ-9", 4, "Minimal"), ("PHQ-9", 5, "Mild"), ("PHQ-9", 10, "Moderate"), ("PHQ-9", 15, "Moderately severe"),
     ("PHQ-9", 27, "Severe"), ("GAD-7", 14, "Moderate"), ("GAD-7", 15, "Severe")],
)  # fmt: skip
def test_severity_bands(kind, score, label):
    assert stats.severity(ASSESSMENTS[kind], score)[0] == label


def test_checkin_summary_uses_the_latest_score_per_kind():
    rows = [
        {"kind": "PHQ-9", "score": 12, "created_at": "2026-09-01 00:00:00"},
        {"kind": "PHQ-9", "score": 4, "created_at": "2026-09-10 00:00:00"},
        {"kind": "GAD-7", "score": 9, "created_at": "2026-09-05 00:00:00"},
    ]
    summary = stats.checkin_summary(rows)
    assert "PHQ-9 4 (Minimal)" in summary and "GAD-7 9 (Mild)" in summary
    assert stats.checkin_summary([]) == ""


def test_journal_summary_counts_recent_entries_and_lists_tags():
    rows = [
        {"tags": "gratitude,routine", "created_at": days_ago(1)},
        {"tags": "work stress", "created_at": days_ago(3)},
        {"tags": "old news", "created_at": days_ago(20)},
    ]
    summary = stats.journal_summary(rows, days=7)
    assert summary.startswith("2 entries in the last 7 days")
    assert "gratitude" in summary and "work stress" in summary and "old news" not in summary
    assert stats.journal_summary([], days=7) == ""


def test_context_summary_combines_sections_and_skips_empty_ones():
    checkins = [{"kind": "GAD-7", "score": 3, "created_at": "2026-09-01 00:00:00"}]
    combined = stats.context_summary(frame(*SAMPLE), checkins, [], date(2026, 9, 7))
    assert "mood — last 7 days" in combined and "check-ins — GAD-7 3 (Minimal)" in combined
    assert "journal" not in combined
    assert stats.context_summary(frame(), [], [], date(2026, 9, 7)) == ""


def test_summary_report_for_a_professional():
    report = stats.summary_markdown(
        "Sam", frame(*SAMPLE), [{"kind": "PHQ-9", "score": 7, "created_at": "2026-09-01 00:00:00"}]
    )
    assert "Wellsy summary for Sam" in report and "7 check-ins" in report
    assert "PHQ-9 = 7" in report and "not a diagnosis" in report
