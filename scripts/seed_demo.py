"""Create a demo account with sample data: python -m scripts.seed_demo"""

import random
from datetime import UTC, datetime, timedelta

from core import auth, db
from core.content import ACTIVITIES, EMOTIONS

LIFTS = {
    "Exercise": 0.9,
    "Friends": 0.7,
    "Outdoors": 0.6,
    "Meditation": 0.4,
    "Screen time": -0.5,
    "Work or study": -0.3,
}
UP, DOWN = ["Calm", "Happy", "Grateful", "Hopeful", "Energetic"], ["Anxious", "Stressed", "Sad", "Tired", "Overwhelmed"]


def stamp(days_ago, hours=0):
    return (datetime.now(UTC) - timedelta(days=days_ago, hours=hours)).strftime("%Y-%m-%d %H:%M:%S")


def seed(username="demo", password="demo-password", days=60):
    db.init()
    try:
        user = auth.register(username, password)
    except auth.AuthError:
        user = auth.login(username, password)
    uid, rng = user["id"], random.Random(7)
    db.update_user(uid, display_name="Sam", country="India")
    for day in range(1, days):
        if rng.random() < 0.15:
            continue
        activities, sleep = rng.sample(ACTIVITIES, rng.randint(1, 3)), rng.choice([5.5, 6, 6.5, 7, 7.5, 8])
        score = round(3 + sum(LIFTS.get(a, 0) for a in activities) + (sleep - 7) * 0.3 + rng.gauss(0, 0.6))
        score = min(5, max(1, score))
        pool = UP if score >= 4 else DOWN if score <= 2 else EMOTIONS
        db.insert(
            "moods", user_id=uid, score=score, emotions=",".join(rng.sample(pool, 2)), activities=",".join(activities),
            sleep_hours=sleep, logged_at=stamp(day, rng.randint(0, 8)),
        )  # fmt: skip
    for title, body, days_ago in [
        ("A calmer morning", "Woke up early, walked for twenty minutes and felt lighter than I have all week.", 2),
        ("Gratitude list", "My sister called. The tea was perfect. I finished the report ahead of time.", 6),
    ]:
        db.insert("journal", user_id=uid, title=title, body=body, tags="gratitude,routine", created_at=stamp(days_ago))
    db.insert(
        "thoughts", user_id=uid, situation="Presentation at work", thought="I will forget everything and fail.",
        emotion="Anxious", traps="Catastrophising", evidence_for="I felt shaky last time.",
        evidence_against="I prepared well and have presented before.",
        balanced="I may be nervous, but I know the material.",
        intensity_before=80, intensity_after=45,
    )  # fmt: skip
    for kind, score, days_ago in [
        ("PHQ-9", 9, 40),
        ("PHQ-9", 7, 20),
        ("PHQ-9", 6, 3),
        ("GAD-7", 8, 30),
        ("GAD-7", 6, 4),
    ]:
        db.insert("assessments", user_id=uid, kind=kind, score=score, created_at=stamp(days_ago))
    chat = db.insert("chats", user_id=uid, title="Nervous about my presentation", persona="Wellsy Counselor")
    for role, text in [
        ("user", "I have a big presentation tomorrow and my mind keeps racing."),
        (
            "assistant",
            "That sounds stressful, and it makes sense that your mind is busy. What is the part that worries you most?",
        ),
        ("user", "I'm scared I'll forget everything."),
        (
            "assistant",
            "Many people feel that before speaking. Try a slow breath in for four, out for six. "
            "Shall we practise it together?",
        ),
    ]:
        db.add_message(uid, chat, role, text)
    return user


if __name__ == "__main__":
    seed()
    print("Demo account ready: demo / demo-password")
