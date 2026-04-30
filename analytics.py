from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import statistics
from models import Task, FocusSession, HabitEntry, EnergyLog, Priority


class BehaviourAnalytics:
    """Core intelligence engine for analysing productivity patterns."""

    def __init__(self, tasks: List[Task], sessions: List[FocusSession],
                 habit_entries: List[HabitEntry], energy_logs: List[EnergyLog]):
        self.tasks = tasks
        self.sessions = sessions
        self.habit_entries = habit_entries
        self.energy_logs = energy_logs

    # ─── PRODUCTIVITY SCORE ───────────────────────────────────────────────────

    def compute_productivity_score(self, window_days: int = 7) -> dict:
        cutoff = (date.today() - timedelta(days=window_days)).isoformat()

        recent_tasks = [t for t in self.tasks if t.created_at[:10] >= cutoff]
        completed = [t for t in recent_tasks if t.is_completed]
        completion_rate = len(completed) / max(len(recent_tasks), 1)

        recent_sessions = [s for s in self.sessions
                          if s.started_at[:10] >= cutoff and s.session_type == "work"]
        focus_hours = sum(s.duration_minutes for s in recent_sessions if s.completed) / 60

        recent_habits = [e for e in self.habit_entries if e.date >= cutoff]
        habit_completion = (sum(1 for e in recent_habits if e.completed) /
                           max(len(recent_habits), 1))

        efficiency_scores = [t.efficiency_ratio for t in completed if t.efficiency_ratio]
        avg_efficiency = statistics.mean(efficiency_scores) if efficiency_scores else 0.5

        avg_quality = (statistics.mean([s.quality_score for s in recent_sessions])
                      if recent_sessions else 3) / 5

        interruption_rate = (statistics.mean([s.interruptions for s in recent_sessions])
                            if recent_sessions else 0)
        interruption_score = max(0, 1 - interruption_rate / 5)

        score = (
            completion_rate * 30 +
            min(focus_hours / (window_days * 4), 1) * 25 +
            habit_completion * 20 +
            min(avg_efficiency, 1) * 15 +
            avg_quality * 10 * interruption_score
        )

        return {
            "overall": round(score, 1),
            "completion_rate": round(completion_rate * 100, 1),
            "focus_hours": round(focus_hours, 1),
            "habit_rate": round(habit_completion * 100, 1),
            "avg_efficiency": round(avg_efficiency * 100, 1),
            "avg_quality": round(avg_quality * 5, 1),
            "tasks_completed": len(completed),
            "tasks_total": len(recent_tasks),
            "sessions_completed": len([s for s in recent_sessions if s.completed])
        }

    # ─── PEAK PERFORMANCE HOURS ───────────────────────────────────────────────

    def find_peak_hours(self) -> Dict[int, float]:
        hour_scores: Dict[int, List[float]] = defaultdict(list)
        for session in self.sessions:
            if session.completed and session.session_type == "work":
                hour = datetime.fromisoformat(session.started_at).hour
                score = session.quality_score * (1 - session.interruptions * 0.1)
                hour_scores[hour].append(max(0, score))
        return {h: round(statistics.mean(scores), 2)
                for h, scores in hour_scores.items()}

    # ─── TASK PATTERNS ────────────────────────────────────────────────────────

    def task_completion_by_day(self) -> Dict[str, dict]:
        day_data: Dict[str, dict] = defaultdict(lambda: {"completed": 0, "created": 0})
        for task in self.tasks:
            d = task.created_at[:10]
            day_data[d]["created"] += 1
            if task.is_completed:
                cd = task.completed_at[:10]
                day_data[cd]["completed"] += 1
        return dict(sorted(day_data.items()))

    def category_breakdown(self) -> Dict[str, dict]:
        cats: Dict[str, dict] = defaultdict(lambda: {"total": 0, "completed": 0, "hours": 0})
        for t in self.tasks:
            cats[t.category]["total"] += 1
            if t.is_completed:
                cats[t.category]["completed"] += 1
                cats[t.category]["hours"] += (t.actual_minutes or t.estimated_minutes) / 60
        return dict(cats)

    def priority_analysis(self) -> Dict[str, dict]:
        prio: Dict[str, dict] = defaultdict(lambda: {"total": 0, "completed": 0, "avg_time": []})
        for t in self.tasks:
            p = t.priority.name
            prio[p]["total"] += 1
            if t.is_completed:
                prio[p]["completed"] += 1
                if t.actual_minutes:
                    prio[p]["avg_time"].append(t.actual_minutes)
        return {p: {
            "total": d["total"],
            "completed": d["completed"],
            "completion_rate": round(d["completed"] / max(d["total"], 1) * 100, 1),
            "avg_minutes": round(statistics.mean(d["avg_time"]), 1) if d["avg_time"] else 0
        } for p, d in prio.items()}

    def estimation_accuracy(self) -> dict:
        completed_with_actuals = [t for t in self.tasks
                                  if t.is_completed and t.actual_minutes]
        if not completed_with_actuals:
            return {"accuracy": 0, "avg_overrun": 0, "underestimated_pct": 0}

        ratios = [t.actual_minutes / t.estimated_minutes for t in completed_with_actuals]
        overruns = [r for r in ratios if r > 1]
        return {
            "accuracy": round(100 - abs(1 - statistics.mean(ratios)) * 100, 1),
            "avg_overrun": round((statistics.mean(ratios) - 1) * 100, 1),
            "underestimated_pct": round(len(overruns) / len(ratios) * 100, 1),
            "avg_ratio": round(statistics.mean(ratios), 2)
        }

    # ─── HABIT STREAKS ────────────────────────────────────────────────────────

    def compute_streaks(self) -> Dict[str, dict]:
        habit_entries = defaultdict(dict)
        for e in self.habit_entries:
            habit_entries[e.habit_name][e.date] = e.completed

        streaks = {}
        for habit, date_map in habit_entries.items():
            current_streak = 0
            longest_streak = 0
            temp = 0
            for d in sorted(date_map.keys(), reverse=True):
                if date_map[d]:
                    temp += 1
                    if d >= (date.today() - timedelta(days=current_streak)).isoformat():
                        current_streak = temp
                else:
                    longest_streak = max(longest_streak, temp)
                    if current_streak == temp:
                        current_streak = 0
                    temp = 0
            longest_streak = max(longest_streak, temp)
            total = len(date_map)
            done = sum(1 for v in date_map.values() if v)
            streaks[habit] = {
                "current_streak": current_streak,
                "longest_streak": longest_streak,
                "completion_rate": round(done / max(total, 1) * 100, 1),
                "total_days": total
            }
        return streaks

    # ─── ENERGY & MOOD CORRELATION ────────────────────────────────────────────

    def energy_productivity_correlation(self) -> dict:
        log_by_date = defaultdict(list)
        for log in self.energy_logs:
            log_by_date[log.date].append(log)

        session_by_date = defaultdict(list)
        for s in self.sessions:
            if s.session_type == "work" and s.completed:
                session_by_date[s.started_at[:10]].append(s)

        correlations = []
        for d in log_by_date:
            if d in session_by_date:
                avg_energy = statistics.mean([l.energy_level.value for l in log_by_date[d]])
                avg_quality = statistics.mean([s.quality_score for s in session_by_date[d]])
                correlations.append((avg_energy, avg_quality))

        if len(correlations) < 2:
            return {"correlation": 0, "data_points": len(correlations), "trend": "insufficient data"}

        energies = [c[0] for c in correlations]
        qualities = [c[1] for c in correlations]

        n = len(correlations)
        mean_e, mean_q = statistics.mean(energies), statistics.mean(qualities)
        cov = sum((e - mean_e) * (q - mean_q) for e, q in correlations) / n
        std_e = statistics.stdev(energies) if len(energies) > 1 else 1
        std_q = statistics.stdev(qualities) if len(qualities) > 1 else 1
        corr = cov / (std_e * std_q) if std_e * std_q > 0 else 0

        return {
            "correlation": round(corr, 3),
            "data_points": n,
            "trend": "positive" if corr > 0.3 else "negative" if corr < -0.3 else "neutral",
            "avg_energy": round(statistics.mean(energies), 2),
            "avg_quality": round(statistics.mean(qualities), 2)
        }

    def energy_by_hour(self) -> Dict[int, float]:
        hour_energy = defaultdict(list)
        for log in self.energy_logs:
            hour = int(log.time.split(":")[0])
            hour_energy[hour].append(log.energy_level.value)
        return {h: round(statistics.mean(v), 2) for h, v in hour_energy.items()}

    # ─── BEHAVIOURAL INSIGHTS ─────────────────────────────────────────────────

    def detect_patterns(self) -> List[dict]:
        patterns = []
        score = self.compute_productivity_score()

        if score["completion_rate"] < 50:
            patterns.append({
                "type": "warning",
                "title": "Low Task Completion",
                "message": f"Only {score['completion_rate']}% of tasks completed this week. "
                          "Consider breaking tasks into smaller, actionable chunks.",
                "icon": "⚠️"
            })

        if score["focus_hours"] < 2:
            patterns.append({
                "type": "alert",
                "title": "Insufficient Deep Work",
                "message": f"Only {score['focus_hours']}h of focused work logged. "
                          "Schedule at least 2-4 deep work blocks daily.",
                "icon": "🎯"
            })

        accuracy = self.estimation_accuracy()
        if accuracy["avg_overrun"] > 30:
            patterns.append({
                "type": "insight",
                "title": "Consistent Time Underestimation",
                "message": f"Tasks take {accuracy['avg_overrun']}% longer than estimated. "
                          "Apply Hofstadter's Law: add 30-50% buffer to all estimates.",
                "icon": "🕐"
            })

        peak = self.find_peak_hours()
        if peak:
            best_hour = max(peak, key=peak.get)
            patterns.append({
                "type": "success",
                "title": "Peak Performance Window",
                "message": f"Your highest-quality work happens around {best_hour}:00. "
                          "Schedule your most demanding tasks in this window.",
                "icon": "⚡"
            })

        streaks = self.compute_streaks()
        broken = [h for h, s in streaks.items() if s["current_streak"] == 0 and s["total_days"] > 3]
        if broken:
            patterns.append({
                "type": "warning",
                "title": "Broken Habit Streaks",
                "message": f"Habits with broken streaks: {', '.join(broken[:3])}. "
                          "Use habit stacking to rebuild momentum.",
                "icon": "🔗"
            })

        corr = self.energy_productivity_correlation()
        if corr["trend"] == "positive" and corr["data_points"] >= 3:
            patterns.append({
                "type": "insight",
                "title": "Energy-Productivity Link",
                "message": f"Strong correlation ({corr['correlation']}) between your energy levels "
                          "and work quality. Prioritise sleep and exercise.",
                "icon": "💡"
            })

        return patterns

    def weekly_summary(self, window_days: int = 7) -> dict:
        score = self.compute_productivity_score(window_days)
        patterns = self.detect_patterns()
        streaks = self.compute_streaks()
        cats = self.category_breakdown()
        prio = self.priority_analysis()

        top_habit = max(streaks.items(), key=lambda x: x[1]["current_streak"]) if streaks else None

        return {
            "score": score,
            "patterns": patterns,
            "top_category": max(cats.items(), key=lambda x: x[1]["completed"]) if cats else None,
            "top_habit": top_habit,
            "priority_stats": prio,
            "estimation_accuracy": self.estimation_accuracy()
        }
