import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date, timedelta
import uuid
import time
import json
import os
from typing import Optional

from models import (Task, FocusSession, HabitEntry, EnergyLog,
                    Priority, EnergyLevel, MoodState, DataStore)
from analytics import BehaviourAnalytics
from ai_insights import AIInsightsEngine

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Productivity Optimizer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0a0a0f;
        --bg-secondary: #111118;
        --bg-card: #16161f;
        --accent: #f59e0b;
        --accent-dim: rgba(245,158,11,0.12);
        --text-primary: #f0f0f5;
        --text-secondary: #8888a0;
        --border: rgba(255,255,255,0.06);
        --success: #10b981;
        --warning: #f59e0b;
        --danger: #ef4444;
        --info: #6366f1;
    }

    .stApp { background: var(--bg-primary) !important; }

    .main .block-container {
        padding: 1.5rem 2rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border) !important;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        color: var(--text-primary) !important;
    }

    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 1.25rem 1.5rem;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 2px;
        background: linear-gradient(90deg, var(--accent), transparent);
    }

    .metric-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--accent);
        line-height: 1;
    }

    .metric-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 0.4rem;
        font-family: 'Space Grotesk', sans-serif;
    }

    .insight-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
    }

    .insight-card.warning { border-left: 3px solid var(--warning); }
    .insight-card.success { border-left: 3px solid var(--success); }
    .insight-card.alert   { border-left: 3px solid var(--danger); }
    .insight-card.insight { border-left: 3px solid var(--info); }

    .score-ring {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 120px; height: 120px;
        border-radius: 50%;
        border: 4px solid var(--accent);
        margin: 0 auto;
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--accent);
        background: var(--accent-dim);
    }

    .tag {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .tag-high { background: rgba(239,68,68,0.15); color: #ef4444; }
    .tag-medium { background: rgba(245,158,11,0.15); color: #f59e0b; }
    .tag-low { background: rgba(16,185,129,0.15); color: #10b981; }
    .tag-critical { background: rgba(239,68,68,0.3); color: #ff6b6b; }

    .timer-display {
        font-family: 'JetBrains Mono', monospace;
        font-size: 4rem;
        font-weight: 700;
        color: var(--accent);
        text-align: center;
        letter-spacing: 0.05em;
    }

    .habit-dot {
        width: 20px; height: 20px;
        border-radius: 4px;
        display: inline-block;
    }

    div[data-testid="stMetricValue"] {
        color: var(--accent) !important;
        font-family: 'JetBrains Mono', monospace !important;
    }

    .stButton > button {
        background: var(--accent-dim) !important;
        color: var(--accent) !important;
        border: 1px solid rgba(245,158,11,0.3) !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }

    .stButton > button:hover {
        background: rgba(245,158,11,0.25) !important;
        border-color: var(--accent) !important;
    }

    div[data-baseweb="select"] > div {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
    }

    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: var(--bg-card) !important;
        border-color: var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }

    .stSlider > div { color: var(--accent) !important; }

    div[data-testid="stExpander"] {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 10px;
    }

    .plotly-chart-div { border-radius: 12px; overflow: hidden; }

    .section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.15em;
        border-bottom: 1px solid var(--border);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY THEME ─────────────────────────────────────────────────────────────

CHART_THEME = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#8888a0", family="JetBrains Mono"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.04)", linecolor="rgba(255,255,255,0.08)"),
    colorway=["#f59e0b", "#6366f1", "#10b981", "#ef4444", "#8b5cf6"]
)

# ─── STATE & DATA ─────────────────────────────────────────────────────────────

if "store" not in st.session_state:
    st.session_state.store = DataStore()

if "timer_running" not in st.session_state:
    st.session_state.timer_running = False
    st.session_state.timer_remaining = 0
    st.session_state.timer_type = "work"
    st.session_state.active_session_id = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "ai_api_key" not in st.session_state:
    st.session_state.ai_api_key = os.environ.get("ANTHROPIC_API_KEY", "")

store = st.session_state.store


def get_analytics() -> BehaviourAnalytics:
    return BehaviourAnalytics(
        store.get_tasks(),
        store.get_focus_sessions(),
        store.get_habit_entries(),
        store.get_energy_logs()
    )


def get_ai() -> Optional[AIInsightsEngine]:
    try:
        return AIInsightsEngine(st.session_state.ai_api_key or None)
    except Exception:
        return None


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0; text-align: center;'>
        <div style='font-family: JetBrains Mono; font-size: 1.1rem; color: #f59e0b; 
                    font-weight: 700; letter-spacing: 0.1em;'>⚡ PRODUCTIVITY</div>
        <div style='font-family: JetBrains Mono; font-size: 0.65rem; color: #555566;
                    letter-spacing: 0.2em; margin-top: 2px;'>BEHAVIOUR INTELLIGENCE SYSTEM</div>
    </div>
    """, unsafe_allow_html=True)

    page = st.selectbox("Navigation", [
        "🏠 Dashboard",
        "✅ Tasks",
        "⏱️ Focus Timer",
        "🔄 Habits",
        "⚡ Energy & Mood",
        "📊 Analytics",
        "🤖 AI Coach",
        "⚙️ Settings"
    ], label_visibility="collapsed")

    st.markdown("---")

    analytics = get_analytics()
    score = analytics.compute_productivity_score()

    st.markdown(f"""
    <div class='metric-card' style='text-align: center; margin-bottom: 1rem;'>
        <div class='score-ring'>{score['overall']:.0f}</div>
        <div class='metric-label' style='text-align: center; margin-top: 0.5rem;'>Productivity Score</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tasks Done", score["tasks_completed"])
        st.metric("Focus Hrs", f"{score['focus_hours']}h")
    with col2:
        st.metric("Completion", f"{score['completion_rate']}%")
        st.metric("Habit Rate", f"{score['habit_rate']}%")

    st.markdown("---")
    st.caption("API Key (optional)")
    api_input = st.text_input("Anthropic API Key", type="password",
                               value=st.session_state.ai_api_key,
                               placeholder="sk-ant-...", label_visibility="collapsed")
    if api_input != st.session_state.ai_api_key:
        st.session_state.ai_api_key = api_input


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

if page == "🏠 Dashboard":
    st.markdown("## Command Center")

    analytics = get_analytics()
    score = analytics.compute_productivity_score()

    col1, col2, col3, col4, col5 = st.columns(5)
    metrics = [
        ("Productivity Score", f"{score['overall']:.0f}/100", ""),
        ("Tasks Completed", f"{score['tasks_completed']}/{score['tasks_total']}", ""),
        ("Focus Hours", f"{score['focus_hours']}h", ""),
        ("Habit Completion", f"{score['habit_rate']}%", ""),
        ("Avg Quality", f"{score['avg_quality']}/5", ""),
    ]
    for col, (label, value, delta) in zip([col1, col2, col3, col4, col5], metrics):
        with col:
            st.metric(label, value)

    st.markdown("---")

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("#### 📅 Task Completion (Last 14 Days)")
        day_data = analytics.task_completion_by_day()
        today = date.today()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(13, -1, -1)]
        created = [day_data.get(d, {}).get("created", 0) for d in dates]
        completed_vals = [day_data.get(d, {}).get("completed", 0) for d in dates]
        short_dates = [d[5:] for d in dates]

        fig = go.Figure()
        fig.add_trace(go.Bar(name="Created", x=short_dates, y=created,
                            marker_color="rgba(99,102,241,0.6)"))
        fig.add_trace(go.Bar(name="Completed", x=short_dates, y=completed_vals,
                            marker_color="rgba(245,158,11,0.8)"))
        fig.update_layout(**CHART_THEME, height=280, barmode="group",
                         legend=dict(orientation="h", y=1.1),
                         margin=dict(l=0, r=0, t=20, b=0))
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        st.markdown("#### 🎯 Priority Breakdown")
        prio = analytics.priority_analysis()
        if prio:
            labels = list(prio.keys())
            values = [v["completion_rate"] for v in prio.values()]
            colors = {"LOW": "#10b981", "MEDIUM": "#f59e0b",
                     "HIGH": "#f97316", "CRITICAL": "#ef4444"}
            fig = go.Figure(go.Bar(
                x=values, y=labels, orientation="h",
                marker_color=[colors.get(l, "#6366f1") for l in labels],
                text=[f"{v:.0f}%" for v in values], textposition="inside"
            ))
            fig.update_layout(**CHART_THEME, height=280,
                             xaxis_title="Completion %",
                             margin=dict(l=0, r=0, t=20, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Add tasks to see priority breakdown")

    st.markdown("---")
    st.markdown("#### 🧠 Behavioural Patterns Detected")
    patterns = analytics.detect_patterns()
    if patterns:
        for p in patterns:
            card_class = p.get("type", "insight")
            st.markdown(f"""
            <div class='insight-card {card_class}'>
                <strong style='color: #f0f0f5;'>{p['icon']} {p['title']}</strong><br>
                <span style='color: #8888a0; font-size: 0.88rem;'>{p['message']}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 Log more data to detect behavioural patterns")

    tasks = store.get_tasks()
    pending = [t for t in tasks if not t.is_completed]
    if pending:
        st.markdown("---")
        st.markdown("#### 📋 Today's Focus — Top Priorities")
        top = sorted(pending, key=lambda t: t.priority.value, reverse=True)[:5]
        for t in top:
            priority_colors = {"CRITICAL": "critical", "HIGH": "high",
                              "MEDIUM": "medium", "LOW": "low"}
            tag_class = priority_colors.get(t.priority.name, "low")
            col_a, col_b, col_c = st.columns([4, 1, 1])
            with col_a:
                st.markdown(f"<span class='tag tag-{tag_class}'>{t.priority.name}</span> "
                          f"**{t.title}** <span style='color:#555566;font-size:0.8rem;'>"
                          f"[{t.category}]</span>", unsafe_allow_html=True)
            with col_b:
                st.caption(f"⏱ {t.estimated_minutes}m")
            with col_c:
                if st.button("✓ Done", key=f"dash_done_{t.id}"):
                    t.completed_at = datetime.now().isoformat()
                    actual = st.session_state.get(f"actual_{t.id}", t.estimated_minutes)
                    t.actual_minutes = actual
                    store.update_task(t)
                    st.rerun()


# ─── TASKS ────────────────────────────────────────────────────────────────────

elif page == "✅ Tasks":
    st.markdown("## Task Manager")

    tab1, tab2 = st.tabs(["📋 Active Tasks", "➕ Add Task"])

    with tab1:
        tasks = store.get_tasks()
        pending = [t for t in tasks if not t.is_completed]
        done = [t for t in tasks if t.is_completed]

        filter_col1, filter_col2 = st.columns([2, 2])
        with filter_col1:
            prio_filter = st.multiselect("Filter Priority",
                                          ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                                          default=["CRITICAL", "HIGH", "MEDIUM", "LOW"])
        with filter_col2:
            categories = list(set(t.category for t in tasks)) or ["General"]
            cat_filter = st.multiselect("Filter Category", categories, default=categories)

        filtered = [t for t in pending
                   if t.priority.name in prio_filter and t.category in cat_filter]
        filtered.sort(key=lambda t: t.priority.value, reverse=True)

        if not filtered:
            st.info("🎉 No pending tasks! Add some above.")
        else:
            for task in filtered:
                with st.expander(f"{'🔴' if task.priority == Priority.CRITICAL else '🟠' if task.priority == Priority.HIGH else '🟡' if task.priority == Priority.MEDIUM else '🟢'} {task.title} — [{task.category}] · ~{task.estimated_minutes}m"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    with col1:
                        st.caption(f"Created: {task.created_at[:16]}")
                        if task.notes:
                            st.caption(f"Notes: {task.notes}")
                    with col2:
                        actual = st.number_input("Actual mins", min_value=1,
                                                value=task.estimated_minutes,
                                                key=f"actual_{task.id}")
                    with col3:
                        st.write("")
                        st.write("")
                        if st.button("✅ Mark Complete", key=f"complete_{task.id}"):
                            task.completed_at = datetime.now().isoformat()
                            task.actual_minutes = actual
                            store.update_task(task)
                            st.success("Task completed!")
                            st.rerun()
                        if st.button("🗑 Delete", key=f"delete_{task.id}"):
                            store.delete_task(task.id)
                            st.rerun()

        st.markdown(f"---\n#### ✓ Completed ({len(done)} tasks)")
        for task in done[-10:]:
            eff = task.efficiency_ratio
            eff_str = f" · Efficiency: {eff:.1f}x" if eff else ""
            st.caption(f"✓ {task.title} · {task.actual_minutes}m actual{eff_str}")

    with tab2:
        st.markdown("#### New Task")
        with st.form("add_task_form"):
            title = st.text_input("Task Title *", placeholder="e.g. Write Q3 report")
            col1, col2 = st.columns(2)
            with col1:
                priority = st.selectbox("Priority", ["LOW", "MEDIUM", "HIGH", "CRITICAL"])
                estimated = st.number_input("Estimated minutes", min_value=5, value=30, step=5)
            with col2:
                category = st.text_input("Category", placeholder="e.g. Work, Learning, Health")
                notes = st.text_area("Notes (optional)", height=80)

            submitted = st.form_submit_button("➕ Add Task")
            if submitted and title:
                task = Task(
                    id=str(uuid.uuid4())[:8],
                    title=title,
                    priority=Priority[priority],
                    category=category or "General",
                    estimated_minutes=estimated,
                    notes=notes
                )
                store.add_task(task)
                st.success(f"✅ Task '{title}' added!")
                st.rerun()


# ─── FOCUS TIMER ─────────────────────────────────────────────────────────────

elif page == "⏱️ Focus Timer":
    st.markdown("## Focus Timer")
    settings = store.get_settings()

    col_main, col_side = st.columns([2, 1])

    with col_main:
        timer_type = st.radio("Session Type",
                             ["🎯 Work", "☕ Short Break", "🌿 Long Break"],
                             horizontal=True)

        durations = {
            "🎯 Work": settings.get("work_duration", 25),
            "☕ Short Break": settings.get("short_break", 5),
            "🌿 Long Break": settings.get("long_break", 15)
        }
        duration = durations[timer_type]

        if not st.session_state.timer_running:
            st.session_state.timer_remaining = duration * 60

        mins = st.session_state.timer_remaining // 60
        secs = st.session_state.timer_remaining % 60

        st.markdown(f"""
        <div style='background: #16161f; border: 1px solid rgba(245,158,11,0.2);
                    border-radius: 20px; padding: 3rem; text-align: center; margin: 1rem 0;'>
            <div class='timer-display'>{mins:02d}:{secs:02d}</div>
            <div style='color: #555566; font-size: 0.8rem; margin-top: 0.5rem; 
                       font-family: JetBrains Mono;'>{timer_type}</div>
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("▶ Start" if not st.session_state.timer_running else "⏸ Pause",
                        use_container_width=True):
                st.session_state.timer_running = not st.session_state.timer_running
                if st.session_state.timer_running and not st.session_state.active_session_id:
                    session_id = str(uuid.uuid4())[:8]
                    st.session_state.active_session_id = session_id
                    session_type_map = {
                        "🎯 Work": "work", "☕ Short Break": "short_break",
                        "🌿 Long Break": "long_break"
                    }
                    session = FocusSession(
                        id=session_id,
                        task_id=st.session_state.get("focus_task_id"),
                        duration_minutes=duration,
                        session_type=session_type_map[timer_type]
                    )
                    store.add_focus_session(session)
        with col_b2:
            if st.button("⏹ Reset", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_remaining = duration * 60
                st.session_state.active_session_id = None
        with col_b3:
            if st.button("✓ Complete", use_container_width=True):
                if st.session_state.active_session_id:
                    sessions = store.get_focus_sessions()
                    for s in sessions:
                        if s.id == st.session_state.active_session_id:
                            s.completed = True
                            store.update_focus_session(s)
                            break
                st.session_state.timer_running = False
                st.session_state.timer_remaining = duration * 60
                st.session_state.active_session_id = None
                st.success("🎉 Session completed!")
                st.rerun()

        if st.session_state.timer_running:
            time.sleep(1)
            st.session_state.timer_remaining = max(0, st.session_state.timer_remaining - 1)
            if st.session_state.timer_remaining == 0:
                st.session_state.timer_running = False
                st.balloons()
            st.rerun()

    with col_side:
        st.markdown("#### Link to Task")
        tasks = store.get_tasks()
        pending = [t for t in tasks if not t.is_completed]
        if pending:
            task_options = {f"{t.title} [{t.priority.name}]": t.id for t in pending}
            selected = st.selectbox("Select task", ["None"] + list(task_options.keys()))
            st.session_state.focus_task_id = task_options.get(selected)

        st.markdown("---")
        st.markdown("#### Today's Sessions")
        today = date.today().isoformat()
        today_sessions = [s for s in store.get_focus_sessions()
                         if s.started_at[:10] == today]
        work_sessions = [s for s in today_sessions if s.session_type == "work"]
        total_focus = sum(s.duration_minutes for s in work_sessions if s.completed)

        st.metric("Work Sessions", len([s for s in work_sessions if s.completed]))
        st.metric("Total Focus", f"{total_focus}m")

        analytics = get_analytics()
        peak_hours = analytics.find_peak_hours()
        if peak_hours:
            best = max(peak_hours, key=peak_hours.get)
            current_hour = datetime.now().hour
            if abs(current_hour - best) <= 1:
                st.success(f"⚡ Peak hour! ({best}:00 is your best window)")
            else:
                st.info(f"🎯 Your peak window: {best}:00")


# ─── HABITS ───────────────────────────────────────────────────────────────────

elif page == "🔄 Habits":
    st.markdown("## Habit Tracker")

    tab1, tab2 = st.tabs(["📅 Daily Log", "📊 Streaks & Stats"])

    with tab1:
        habits = store.get_habits()
        today = date.today().isoformat()

        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            new_habit = st.text_input("New habit", placeholder="e.g. Morning meditation, 30min reading...")
        with col_h2:
            st.write("")
            if st.button("+ Add Habit") and new_habit:
                store.add_habit(new_habit)
                st.rerun()

        if not habits:
            st.info("Add your first habit above!")
        else:
            st.markdown(f"#### Today — {today}")
            entries = {e.habit_name: e for e in store.get_habit_entries() if e.date == today}

            for habit in habits:
                col_a, col_b, col_c = st.columns([4, 1, 1])
                with col_a:
                    done = entries.get(habit, HabitEntry(habit, today, False)).completed
                    st.markdown(
                        f"<span style='color: {'#10b981' if done else '#555566'};'>{'✅' if done else '⬜'}</span> "
                        f"<span style='color: #f0f0f5;'>{habit}</span>",
                        unsafe_allow_html=True
                    )
                with col_b:
                    if st.button("✓ Done" if not done else "↺ Undo", key=f"habit_{habit}"):
                        entry = HabitEntry(habit_name=habit, date=today, completed=not done)
                        store.log_habit(entry)
                        st.rerun()
                with col_c:
                    if st.button("🗑", key=f"del_habit_{habit}"):
                        store.remove_habit(habit)
                        st.rerun()

    with tab2:
        analytics = get_analytics()
        streaks = analytics.compute_streaks()

        if not streaks:
            st.info("Log habits for at least a few days to see streaks!")
        else:
            cols = st.columns(min(len(streaks), 3))
            for i, (habit, stats) in enumerate(streaks.items()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class='metric-card' style='margin-bottom: 1rem;'>
                        <div style='font-size: 0.85rem; color: #f0f0f5; margin-bottom: 0.5rem;'>{habit}</div>
                        <div class='metric-value'>{stats['current_streak']}</div>
                        <div class='metric-label'>Current Streak</div>
                        <div style='margin-top: 0.75rem; display: flex; gap: 1rem;'>
                            <span style='font-size: 0.75rem; color: #8888a0;'>
                                Best: {stats['longest_streak']} days
                            </span>
                            <span style='font-size: 0.75rem; color: #8888a0;'>
                                Rate: {stats['completion_rate']}%
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

            all_entries = store.get_habit_entries()
            if all_entries:
                dates = sorted(set(e.date for e in all_entries))[-30:]
                habits_list = store.get_habits()
                entry_map = {(e.habit_name, e.date): e.completed for e in all_entries}

                z_vals = []
                for habit in habits_list:
                    row = [1 if entry_map.get((habit, d), False) else 0 for d in dates]
                    z_vals.append(row)

                fig = go.Figure(go.Heatmap(
                    z=z_vals,
                    x=[d[5:] for d in dates],
                    y=habits_list,
                    colorscale=[[0, "#1a1a25"], [1, "#f59e0b"]],
                    showscale=False
                ))
                fig.update_layout(**CHART_THEME, height=max(150, len(habits_list) * 50 + 80),
                                 title="30-Day Habit Heatmap",
                                 margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)


# ─── ENERGY & MOOD ────────────────────────────────────────────────────────────

elif page == "⚡ Energy & Mood":
    st.markdown("## Energy & Mood Logger")

    tab1, tab2 = st.tabs(["📝 Log Entry", "📈 Trends"])

    with tab1:
        with st.form("energy_form"):
            col1, col2 = st.columns(2)
            with col1:
                energy = st.select_slider("Energy Level",
                    options=["DEPLETED", "LOW", "MODERATE", "HIGH", "PEAK"], value="MODERATE")
                sleep = st.number_input("Sleep (hours)", min_value=0.0, max_value=12.0,
                                        value=7.0, step=0.5)
            with col2:
                mood = st.select_slider("Mood State",
                    options=["STRESSED", "ANXIOUS", "NEUTRAL", "FOCUSED", "MOTIVATED"],
                    value="NEUTRAL")
                log_time = st.time_input("Time", value=datetime.now().time())

            notes = st.text_input("Notes (optional)", placeholder="What's affecting your energy today?")
            submitted = st.form_submit_button("📊 Log Entry")

            if submitted:
                log = EnergyLog(
                    date=date.today().isoformat(),
                    time=log_time.strftime("%H:%M"),
                    energy_level=EnergyLevel[energy],
                    mood=MoodState[mood],
                    sleep_hours=sleep,
                    notes=notes
                )
                store.add_energy_log(log)
                st.success("✅ Entry logged!")

    with tab2:
        logs = store.get_energy_logs()
        if len(logs) < 2:
            st.info("Log at least 2 entries to see trends!")
        else:
            recent = sorted(logs, key=lambda l: l.date + l.time)[-30:]
            dates_times = [l.date + " " + l.time for l in recent]
            energy_vals = [l.energy_level.value for l in recent]
            mood_vals = [l.mood.value for l in recent]
            sleep_vals = [l.sleep_hours for l in recent]

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates_times, y=energy_vals, name="Energy",
                                    line=dict(color="#f59e0b", width=2),
                                    fill="tonexty", fillcolor="rgba(245,158,11,0.05)"))
            fig.add_trace(go.Scatter(x=dates_times, y=mood_vals, name="Mood",
                                    line=dict(color="#6366f1", width=2, dash="dot")))
            fig.add_trace(go.Scatter(x=dates_times, y=sleep_vals, name="Sleep (hrs)",
                                    line=dict(color="#10b981", width=1.5, dash="dash"),
                                    yaxis="y2"))
            fig.update_layout(
                **CHART_THEME, height=320,
                yaxis=dict(title="Level (1-5)", gridcolor="rgba(255,255,255,0.04)"),
                yaxis2=dict(title="Sleep hrs", overlaying="y", side="right",
                           gridcolor="rgba(255,255,255,0.02)"),
                legend=dict(orientation="h", y=1.1),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)

            analytics = get_analytics()
            corr = analytics.energy_productivity_correlation()
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Energy-Quality Correlation", f"{corr['correlation']:.2f}")
            with col2:
                st.metric("Avg Energy Level", f"{corr.get('avg_energy', 0):.1f}/5")
            with col3:
                trend_icons = {"positive": "📈", "negative": "📉", "neutral": "➡️"}
                st.metric("Trend", f"{trend_icons.get(corr['trend'], '?')} {corr['trend'].title()}")

            energy_by_hr = analytics.energy_by_hour()
            if energy_by_hr:
                fig2 = go.Figure(go.Bar(
                    x=[f"{h:02d}:00" for h in sorted(energy_by_hr.keys())],
                    y=[energy_by_hr[h] for h in sorted(energy_by_hr.keys())],
                    marker_color="rgba(245,158,11,0.7)",
                    marker_line_color="rgba(245,158,11,1)",
                    marker_line_width=1
                ))
                fig2.update_layout(**CHART_THEME, height=250, title="Average Energy by Hour",
                                  margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig2, use_container_width=True)


# ─── ANALYTICS ────────────────────────────────────────────────────────────────

elif page == "📊 Analytics":
    st.markdown("## Deep Analytics")

    analytics = get_analytics()

    tab1, tab2, tab3 = st.tabs(["🎯 Focus Patterns", "📋 Task Intelligence", "🔄 Habit Analytics"])

    with tab1:
        sessions = store.get_focus_sessions()
        work_sessions = [s for s in sessions if s.session_type == "work"]

        col1, col2, col3, col4 = st.columns(4)
        total_work = sum(s.duration_minutes for s in work_sessions if s.completed)
        with col1: st.metric("Total Focus Time", f"{total_work//60}h {total_work%60}m")
        with col2: st.metric("Sessions Done", len([s for s in work_sessions if s.completed]))
        with col3:
            avg_q = (sum(s.quality_score for s in work_sessions) /
                    max(len(work_sessions), 1))
            st.metric("Avg Quality", f"{avg_q:.1f}/5")
        with col4:
            avg_int = (sum(s.interruptions for s in work_sessions) /
                      max(len(work_sessions), 1))
            st.metric("Avg Interruptions", f"{avg_int:.1f}")

        peak_hours = analytics.find_peak_hours()
        if peak_hours:
            all_hours = list(range(6, 23))
            hour_scores = [peak_hours.get(h, 0) for h in all_hours]
            fig = go.Figure(go.Bar(
                x=[f"{h:02d}:00" for h in all_hours],
                y=hour_scores,
                marker_color=[
                    "rgba(245,158,11,0.9)" if peak_hours.get(h, 0) == max(peak_hours.values())
                    else "rgba(99,102,241,0.6)" for h in all_hours
                ]
            ))
            fig.update_layout(**CHART_THEME, title="Peak Performance Hours",
                             height=300, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            cats = analytics.category_breakdown()
            if cats:
                fig = go.Figure(go.Pie(
                    labels=list(cats.keys()),
                    values=[v["total"] for v in cats.values()],
                    hole=0.5,
                    marker=dict(colors=["#f59e0b", "#6366f1", "#10b981",
                                       "#ef4444", "#8b5cf6", "#f97316"])
                ))
                fig.update_layout(**CHART_THEME, title="Tasks by Category",
                                 height=300, margin=dict(l=0, r=0, t=40, b=0))
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            accuracy = analytics.estimation_accuracy()
            st.markdown("#### ⏱ Estimation Accuracy")
            st.metric("Accuracy Score", f"{accuracy['accuracy']}%")
            st.metric("Avg Time Overrun", f"+{accuracy['avg_overrun']}%")
            st.metric("Underestimated Tasks", f"{accuracy['underestimated_pct']}%")

            if accuracy["avg_overrun"] > 20:
                st.warning("💡 You consistently underestimate tasks. Add a 30% buffer.")
            elif accuracy["accuracy"] > 80:
                st.success("✅ Excellent estimation accuracy!")

    with tab3:
        streaks = analytics.compute_streaks()
        if streaks:
            habit_names = list(streaks.keys())
            streak_vals = [v["current_streak"] for v in streaks.values()]
            rate_vals = [v["completion_rate"] for v in streaks.values()]

            fig = go.Figure()
            fig.add_trace(go.Bar(name="Current Streak", x=habit_names, y=streak_vals,
                                marker_color="rgba(245,158,11,0.8)"))
            fig.add_trace(go.Scatter(name="Completion %", x=habit_names, y=rate_vals,
                                    mode="lines+markers", yaxis="y2",
                                    line=dict(color="#10b981", width=2)))
            fig.update_layout(
                **CHART_THEME, title="Habit Performance Overview", height=320,
                yaxis=dict(title="Streak (days)"),
                yaxis2=dict(title="Completion %", overlaying="y", side="right"),
                legend=dict(orientation="h", y=1.1),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)


# ─── AI COACH ─────────────────────────────────────────────────────────────────

elif page == "🤖 AI Coach":
    st.markdown("## AI Behavioural Coach")

    if not st.session_state.ai_api_key and not os.environ.get("ANTHROPIC_API_KEY"):
        st.warning("⚠️ Add your Anthropic API key in the sidebar to use AI features.")
    else:
        analytics = get_analytics()
        score = analytics.compute_productivity_score()
        patterns = analytics.detect_patterns()
        streaks = analytics.compute_streaks()
        weekly = analytics.weekly_summary()

        user_data = {
            "productivity_score": score,
            "behaviour_patterns": patterns,
            "habit_streaks": streaks,
            "weekly_summary": weekly
        }

        tab1, tab2, tab3 = st.tabs(["💬 Chat with Coach", "📋 Daily Brief", "📈 Weekly Strategy"])

        with tab1:
            st.markdown("Ask your AI coach anything about your productivity data and behaviours.")

            for msg in st.session_state.chat_history:
                role = "🧑 You" if msg["role"] == "user" else "🤖 Coach"
                bg = "#16161f" if msg["role"] == "user" else "#1a1a2e"
                st.markdown(f"""
                <div style='background: {bg}; border: 1px solid rgba(255,255,255,0.05);
                            border-radius: 10px; padding: 0.75rem 1rem; margin-bottom: 0.5rem;'>
                    <div style='font-size: 0.7rem; color: #555566; margin-bottom: 0.25rem;'>{role}</div>
                    <div style='color: #f0f0f5; font-size: 0.9rem;'>{msg['content']}</div>
                </div>
                """, unsafe_allow_html=True)

            user_input = st.text_input("Ask your coach...",
                                       placeholder="e.g. Why is my productivity dropping on Fridays?",
                                       key="coach_input")

            col_b1, col_b2 = st.columns([1, 5])
            with col_b1:
                if st.button("Send ↗") and user_input:
                    st.session_state.chat_history.append(
                        {"role": "user", "content": user_input}
                    )
                    with st.spinner("Coach is thinking..."):
                        try:
                            ai = get_ai()
                            response = ai.chat_with_coach(st.session_state.chat_history, user_data)
                            st.session_state.chat_history.append(
                                {"role": "assistant", "content": response}
                            )
                        except Exception as e:
                            st.error(f"API Error: {e}")
                    st.rerun()
            with col_b2:
                if st.button("🗑 Clear Chat"):
                    st.session_state.chat_history = []
                    st.rerun()

        with tab2:
            if st.button("🔄 Generate Daily Brief"):
                with st.spinner("Analysing your patterns..."):
                    try:
                        ai = get_ai()
                        brief = ai.generate_daily_brief(user_data)
                        st.markdown(f"""
                        <div style='background: #16161f; border: 1px solid rgba(245,158,11,0.2);
                                    border-left: 3px solid #f59e0b; border-radius: 10px;
                                    padding: 1.25rem 1.5rem; line-height: 1.7;
                                    color: #d0d0e0;'>
                            {brief}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")

        with tab3:
            if st.button("🔄 Generate Weekly Strategy"):
                with st.spinner("Building your strategy..."):
                    try:
                        ai = get_ai()
                        strategy = ai.generate_weekly_strategy(weekly)
                        st.markdown(f"""
                        <div style='background: #16161f; border: 1px solid rgba(99,102,241,0.2);
                                    border-left: 3px solid #6366f1; border-radius: 10px;
                                    padding: 1.25rem 1.5rem; line-height: 1.7;
                                    color: #d0d0e0;'>
                            {strategy}
                        </div>
                        """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Error: {e}")


# ─── SETTINGS ─────────────────────────────────────────────────────────────────

elif page == "⚙️ Settings":
    st.markdown("## Settings")
    settings = store.get_settings()

    st.markdown("#### 🎯 Pomodoro Configuration")
    with st.form("settings_form"):
        col1, col2 = st.columns(2)
        with col1:
            work = st.number_input("Work duration (min)", min_value=5, max_value=90,
                                   value=settings.get("work_duration", 25))
            short_break = st.number_input("Short break (min)", min_value=1, max_value=30,
                                          value=settings.get("short_break", 5))
        with col2:
            long_break = st.number_input("Long break (min)", min_value=5, max_value=60,
                                         value=settings.get("long_break", 15))
            sessions_before_long = st.number_input("Sessions before long break", min_value=2,
                                                    max_value=8,
                                                    value=settings.get("sessions_before_long_break", 4))
        daily_goal = st.slider("Daily focus goal (hours)", min_value=1, max_value=12,
                               value=settings.get("daily_goal_hours", 6))

        if st.form_submit_button("💾 Save Settings"):
            store.update_settings({
                "work_duration": work,
                "short_break": short_break,
                "long_break": long_break,
                "sessions_before_long_break": sessions_before_long,
                "daily_goal_hours": daily_goal
            })
            st.success("Settings saved!")

    st.markdown("---")
    st.markdown("#### 🗃️ Data Management")
    col1, col2 = st.columns(2)
    with col1:
        if os.path.exists("productivity_data.json"):
            with open("productivity_data.json", "r") as f:
                data_str = f.read()
            st.download_button("⬇️ Export Data (JSON)", data_str,
                              "productivity_data.json", "application/json")
    with col2:
        uploaded = st.file_uploader("⬆️ Import Data", type="json")
        if uploaded:
            data = json.load(uploaded)
            with open("productivity_data.json", "w") as f:
                json.dump(data, f)
            st.session_state.store = DataStore()
            st.success("Data imported! Refreshing...")
            st.rerun()

    if st.button("🗑️ Clear All Data", type="secondary"):
        if st.session_state.get("confirm_clear"):
            if os.path.exists("productivity_data.json"):
                os.remove("productivity_data.json")
            st.session_state.store = DataStore()
            st.success("All data cleared.")
            st.session_state.confirm_clear = False
            st.rerun()
        else:
            st.session_state.confirm_clear = True
            st.warning("⚠️ Click again to confirm deletion of ALL data.")
