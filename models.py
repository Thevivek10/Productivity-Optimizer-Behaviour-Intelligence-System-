from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List
from enum import Enum
import json
import os


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class EnergyLevel(Enum):
    DEPLETED = 1
    LOW = 2
    MODERATE = 3
    HIGH = 4
    PEAK = 5


class MoodState(Enum):
    STRESSED = 1
    ANXIOUS = 2
    NEUTRAL = 3
    FOCUSED = 4
    MOTIVATED = 5


@dataclass
class Task:
    id: str
    title: str
    priority: Priority
    category: str
    estimated_minutes: int
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    actual_minutes: Optional[int] = None
    notes: str = ""

    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None

    @property
    def efficiency_ratio(self) -> Optional[float]:
        if self.actual_minutes and self.estimated_minutes:
            return round(self.estimated_minutes / self.actual_minutes, 2)
        return None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "priority": self.priority.name,
            "category": self.category,
            "estimated_minutes": self.estimated_minutes,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "actual_minutes": self.actual_minutes,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            priority=Priority[data["priority"]],
            category=data["category"],
            estimated_minutes=data["estimated_minutes"],
            created_at=data.get("created_at", datetime.now().isoformat()),
            completed_at=data.get("completed_at"),
            actual_minutes=data.get("actual_minutes"),
            notes=data.get("notes", "")
        )


@dataclass
class FocusSession:
    id: str
    task_id: Optional[str]
    duration_minutes: int
    session_type: str  # "work", "short_break", "long_break"
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed: bool = False
    interruptions: int = 0
    quality_score: int = 3  # 1-5

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "duration_minutes": self.duration_minutes,
            "session_type": self.session_type,
            "started_at": self.started_at,
            "completed": self.completed,
            "interruptions": self.interruptions,
            "quality_score": self.quality_score
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FocusSession":
        return cls(**data)


@dataclass
class HabitEntry:
    habit_name: str
    date: str
    completed: bool
    streak: int = 0
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "habit_name": self.habit_name,
            "date": self.date,
            "completed": self.completed,
            "streak": self.streak,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HabitEntry":
        return cls(**data)


@dataclass
class EnergyLog:
    date: str
    time: str
    energy_level: EnergyLevel
    mood: MoodState
    sleep_hours: float
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "date": self.date,
            "time": self.time,
            "energy_level": self.energy_level.name,
            "mood": self.mood.name,
            "sleep_hours": self.sleep_hours,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "EnergyLog":
        return cls(
            date=data["date"],
            time=data["time"],
            energy_level=EnergyLevel[data["energy_level"]],
            mood=MoodState[data["mood"]],
            sleep_hours=data["sleep_hours"],
            notes=data.get("notes", "")
        )


class DataStore:
    def __init__(self, data_file: str = "productivity_data.json"):
        self.data_file = data_file
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.data_file):
            with open(self.data_file, "r") as f:
                return json.load(f)
        return {
            "tasks": [],
            "focus_sessions": [],
            "habits": [],
            "habit_entries": [],
            "energy_logs": [],
            "settings": {
                "work_duration": 25,
                "short_break": 5,
                "long_break": 15,
                "sessions_before_long_break": 4,
                "daily_goal_hours": 6
            }
        }

    def save(self):
        with open(self.data_file, "w") as f:
            json.dump(self._data, f, indent=2)

    def get_tasks(self) -> List[Task]:
        return [Task.from_dict(t) for t in self._data.get("tasks", [])]

    def add_task(self, task: Task):
        self._data.setdefault("tasks", []).append(task.to_dict())
        self.save()

    def update_task(self, task: Task):
        tasks = self._data.get("tasks", [])
        for i, t in enumerate(tasks):
            if t["id"] == task.id:
                tasks[i] = task.to_dict()
                break
        self.save()

    def delete_task(self, task_id: str):
        self._data["tasks"] = [t for t in self._data.get("tasks", []) if t["id"] != task_id]
        self.save()

    def get_focus_sessions(self) -> List[FocusSession]:
        return [FocusSession.from_dict(s) for s in self._data.get("focus_sessions", [])]

    def add_focus_session(self, session: FocusSession):
        self._data.setdefault("focus_sessions", []).append(session.to_dict())
        self.save()

    def update_focus_session(self, session: FocusSession):
        sessions = self._data.get("focus_sessions", [])
        for i, s in enumerate(sessions):
            if s["id"] == session.id:
                sessions[i] = session.to_dict()
                break
        self.save()

    def get_habits(self) -> List[str]:
        return self._data.get("habits", [])

    def add_habit(self, habit_name: str):
        if habit_name not in self._data.get("habits", []):
            self._data.setdefault("habits", []).append(habit_name)
            self.save()

    def remove_habit(self, habit_name: str):
        self._data["habits"] = [h for h in self._data.get("habits", []) if h != habit_name]
        self.save()

    def get_habit_entries(self) -> List[HabitEntry]:
        return [HabitEntry.from_dict(e) for e in self._data.get("habit_entries", [])]

    def log_habit(self, entry: HabitEntry):
        entries = self._data.get("habit_entries", [])
        existing = next((i for i, e in enumerate(entries)
                        if e["habit_name"] == entry.habit_name and e["date"] == entry.date), None)
        if existing is not None:
            entries[existing] = entry.to_dict()
        else:
            entries.append(entry.to_dict())
        self._data["habit_entries"] = entries
        self.save()

    def get_energy_logs(self) -> List[EnergyLog]:
        return [EnergyLog.from_dict(e) for e in self._data.get("energy_logs", [])]

    def add_energy_log(self, log: EnergyLog):
        self._data.setdefault("energy_logs", []).append(log.to_dict())
        self.save()

    def get_settings(self) -> dict:
        return self._data.get("settings", {})

    def update_settings(self, settings: dict):
        self._data["settings"] = settings
        self.save()
