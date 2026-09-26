"""Static content used across Wellsy pages."""

MOODS = {1: ("😞", "Very low"), 2: ("😕", "Low"), 3: ("😐", "Okay"), 4: ("🙂", "Good"), 5: ("😄", "Great")}
MOOD_COLORS = ["#E76F51", "#F4A261", "#E9C46A", "#8AB17D", "#2A9D8F"]

EMOTIONS = [
    "Calm", "Happy", "Grateful", "Hopeful", "Energetic", "Anxious",
    "Stressed", "Sad", "Angry", "Lonely", "Tired", "Overwhelmed",
]  # fmt: skip
ACTIVITIES = [
    "Exercise", "Work or study", "Friends", "Family", "Outdoors", "Creative time",
    "Meditation", "Reading", "Screen time", "Rest", "Chores",
]  # fmt: skip

AFFIRMATIONS = [
    "You are not alone. Small steps matter.",
    "Healing is not linear. Be gentle with yourself.",
    "It's okay to pause. Progress takes time.",
    "Your feelings are valid.",
    "One step at a time. You are doing enough.",
    "Be as kind to yourself as you would be to a friend.",
    "Feelings come and go, like weather passing through.",
]

FOCUS_TIPS = [
    "Drink a glass of water and take three slow breaths.",
    "Step outside for five minutes of daylight.",
    "Send a friendly message to someone you care about.",
    "Write down one thing that went okay today.",
    "Stretch your shoulders and unclench your jaw.",
    "Choose one small, kind goal for today.",
    "Take a short break from screens.",
]

JOURNAL_PROMPTS = {
    "Free write": "Write whatever is on your mind.",
    "Gratitude": "Three things I'm grateful for today, and why.",
    "One small win": "Something I handled well today, however small.",
    "What's weighing on me": "What feels heavy right now, and what would help lighten it?",
    "Kind words": "What would I say to a friend who felt the way I do?",
    "Letter to future me": "What do I want my future self to remember?",
}

# name -> (description, [(phase label, seconds, circle scale reached at the end of the phase)])
BREATHING = {
    "Box breathing": (
        "Steady and focusing. Useful before a stressful moment.",
        [("Breathe in", 4, 1.0), ("Hold", 4, 1.0), ("Breathe out", 4, 0.6), ("Hold", 4, 0.6)],
    ),
    "4-7-8 relaxing": (
        "A long exhale that helps the body slow down, often used before sleep.",
        [("Breathe in", 4, 1.0), ("Hold", 7, 1.0), ("Breathe out", 8, 0.6)],
    ),
    "Calm 5-5": (
        "Gentle paced breathing at about six breaths per minute.",
        [("Breathe in", 5, 1.0), ("Breathe out", 5, 0.6)],
    ),
}

GROUNDING = [
    (5, "You can see"), (4, "You can feel"), (3, "You can hear"), (2, "You can smell"), (1, "You can taste"),
]  # fmt: skip

THINKING_TRAPS = [
    "All-or-nothing", "Catastrophising", "Mind reading", "Overgeneralising",
    "Should statements", "Emotional reasoning", "Personalising", "Discounting the positive",
]  # fmt: skip

SAFETY_PLAN_STEPS = {
    "warning_signs": "Warning signs: thoughts, moods or situations that tell me a crisis may be building",
    "coping": "Things I can do on my own to take my mind off my problems",
    "distraction": "People and places that help me feel better",
    "people": "People I can ask for help",
    "professionals": "Professionals or services I can contact",
    "safe_space": "Ways I can make my surroundings safer",
}

ANSWERS = ["Not at all", "Several days", "More than half the days", "Nearly every day"]

# PHQ-9 and GAD-7 are free-to-use screening questionnaires (Spitzer, Williams, Kroenke et al.).
# Bands: (max score, label, guidance).
ASSESSMENTS = {
    "PHQ-9": {
        "title": "Mood check (PHQ-9)",
        "questions": [
            "Little interest or pleasure in doing things",
            "Feeling down, depressed, or hopeless",
            "Trouble falling or staying asleep, or sleeping too much",
            "Feeling tired or having little energy",
            "Poor appetite or overeating",
            "Feeling bad about yourself, or that you are a failure or have let yourself or your family down",
            "Trouble concentrating on things, such as reading or watching television",
            "Moving or speaking so slowly that others could notice, "
            "or being so restless that you move around a lot more than usual",
            "Thoughts that you would be better off dead, or of hurting yourself in some way",
        ],
        "risk_item": 8,
        "bands": [
            (4, "Minimal", "Few symptoms right now. Keep up the habits that support you."),
            (9, "Mild", "Some symptoms are present. Tracking your mood and self-care can help."),
            (14, "Moderate", "Symptoms may be affecting daily life. Consider talking to a doctor or counsellor."),
            (
                19,
                "Moderately severe",
                "Symptoms are likely affecting your life. Please consider speaking to a professional soon.",
            ),
            (
                27,
                "Severe",
                "Symptoms may be significantly affecting your life. Please reach out to a mental health professional.",
            ),
        ],
    },
    "GAD-7": {
        "title": "Anxiety check (GAD-7)",
        "questions": [
            "Feeling nervous, anxious, or on edge",
            "Not being able to stop or control worrying",
            "Worrying too much about different things",
            "Trouble relaxing",
            "Being so restless that it is hard to sit still",
            "Becoming easily annoyed or irritable",
            "Feeling afraid, as if something awful might happen",
        ],
        "risk_item": None,
        "bands": [
            (4, "Minimal", "Few symptoms right now. Keep up the habits that support you."),
            (9, "Mild", "Some symptoms are present. Breathing and grounding exercises can help."),
            (14, "Moderate", "Symptoms may be affecting daily life. Consider talking to a doctor or counsellor."),
            (
                21,
                "Severe",
                "Symptoms may be significantly affecting your life. Please reach out to a mental health professional.",
            ),
        ],
    },
}
