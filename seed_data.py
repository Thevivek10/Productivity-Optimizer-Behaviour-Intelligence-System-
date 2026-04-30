"""
Run this script to populate the app with realistic demo data.
Usage: python seed_data.py
"""
import sys
sys.path.insert(0, ".")

from models import (Task, FocusSession, HabitEntry, EnergyLog,
                    Priority, EnergyLevel, MoodState, DataStore)
from datetime import datetime, date, timedelta
import random
import uuid

store = DataStore()
today = date.today()

# ─── TASKS ───────────────────────────────────────────────────────────────────
task_templates = [
    ("Design system architecture for new feature", Priority.CRITICAL, "Engineering", 90),
    ("Write unit tests for auth module", Priority.HIGH, "Engineering", 60),
    ("Review pull requests", Priority.HIGH, "Engineering", 45),
    ("Update project documentation", Priority.MEDIUM, "Engineering", 30),
    ("Prepare Q3 performance report", Priority.HIGH, "Strategy", 120),
    ("Weekly team standup preparation", Priority.MEDIUM, "Meetings", 20),
    ("Read 'Deep Work' — chapter 4", Priority.LOW, "Learning", 45),
    ("Gym workout session", Priority.HIGH, "Health", 60),
    ("Meditate for 15 minutes", Priority.MEDIUM, "Health", 15),
    ("Respond to stakeholder emails", Priority.MEDIUM, "Communication", 30),
    ("Refactor database query layer", Priority.HIGH, "Engineering", 90),
    ("Plan next sprint backlog", Priority.MEDIUM, "Strategy", 60),
    ("Study Rust ownership model", Priority.LOW, "Learning", 60),
    ("Code review — ML pipeline PR", Priority.HIGH, "Engineering", 45),
    ("Prepare presentation slides", Priority.CRITICAL, "Communication", 90),
]

print("Creating tasks...")
for i, (title, priority, category, est) in enumerate(task_templates):
    task = Task(
        id=str(uuid.uuid4())[:8],
        title=title,
        priority=priority,
        category=category,
        estimated_minutes=est,
        created_at=(today - timedelta(days=random.randint(0, 14))).isoformat() + "T09:00:00",
    )
    if random.random() < 0.65:
        days_ago = random.randint(0, 10)
        task.completed_at = (today - timedelta(days=days_ago)).isoformat() + "T15:30:00"
        overrun = random.gauss(1.15, 0.25)
        task.actual_minutes = max(5, int(est * max(0.5, overrun)))
    store.add_task(task)

# ─── FOCUS SESSIONS ──────────────────────────────────────────────────────────
print("Creating focus sessions...")
session_hours = [9, 10, 14, 15, 16]
for day_offset in range(14):
    session_date = today - timedelta(days=day_offset)
    num_sessions = random.randint(2, 5)
    for _ in range(num_sessions):
        hour = random.choice(session_hours)
        session = FocusSession(
            id=str(uuid.uuid4())[:8],
            task_id=None,
            duration_minutes=25,
            session_type="work",
            started_at=session_date.isoformat() + f"T{hour:02d}:00:00",
            completed=random.random() < 0.85,
            interruptions=random.randint(0, 3),
            quality_score=random.randint(2, 5)
        )
        store.add_focus_session(session)

# ─── HABITS ──────────────────────────────────────────────────────────────────
habits = ["Morning meditation", "Daily exercise", "Reading 30min", "No screens after 10pm",
          "Drink 2L water", "Review daily goals"]
print("Creating habits...")
for habit in habits:
    store.add_habit(habit)

for day_offset in range(30):
    habit_date = (today - timedelta(days=day_offset)).isoformat()
    for habit in habits:
        completion_prob = 0.75 if "exercise" in habit else 0.85
        entry = HabitEntry(
            habit_name=habit,
            date=habit_date,
            completed=random.random() < completion_prob
        )
        store.log_habit(entry)

# ─── ENERGY LOGS ─────────────────────────────────────────────────────────────
print("Creating energy logs...")
for day_offset in range(21):
    log_date = (today - timedelta(days=day_offset)).isoformat()
    sleep = random.gauss(7.0, 1.0)
    sleep = max(4.0, min(9.0, sleep))

    for time_str in ["08:00", "13:00", "17:00"]:
        hour = int(time_str[:2])
        if hour == 8:
            energy_base = 3 + (sleep - 6) * 0.5
        elif hour == 13:
            energy_base = 2.5
        else:
            energy_base = 3.5 + (sleep - 6) * 0.3

        energy_val = max(1, min(5, int(energy_base + random.gauss(0, 0.5))))
        mood_val = max(1, min(5, int(energy_val + random.randint(-1, 1))))

        log = EnergyLog(
            date=log_date,
            time=time_str,
            energy_level=EnergyLevel(energy_val),
            mood=MoodState(mood_val),
            sleep_hours=round(sleep, 1)
        )
        store.add_energy_log(log)

print("\n✅ Demo data created successfully!")
print("Run: streamlit run app.py")
