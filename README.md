# ⚡ Productivity Optimizer — Behaviour Intelligence System

A Python-powered productivity system with AI behavioural coaching, built with Streamlit.

## Features

| Module | Description |
|--------|-------------|
| 🏠 **Dashboard** | Live productivity score, task completion charts, detected behavioural patterns |
| ✅ **Tasks** | Priority-based task management with estimation accuracy tracking |
| ⏱️ **Focus Timer** | Pomodoro timer with session quality scoring and peak-hour detection |
| 🔄 **Habits** | Daily habit logging, streaks, 30-day heatmaps |
| ⚡ **Energy & Mood** | Energy/mood logging with productivity correlation analysis |
| 📊 **Analytics** | Deep behavioural analytics — focus patterns, category breakdown, estimation accuracy |
| 🤖 **AI Coach** | Claude-powered coaching: daily briefs, weekly strategies, interactive chat |
| ⚙️ **Settings** | Pomodoro config, data import/export |

## Quickstart

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (Optional) Set your Anthropic API key for AI features
export ANTHROPIC_API_KEY=sk-ant-...

# 3. (Optional) Populate with demo data
python seed_data.py

# 4. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`
## Project Structure

```
productivity_optimizer/
├── app.py              # Main Streamlit UI (all pages)
├── models.py           # Data models (Task, FocusSession, HabitEntry, EnergyLog)
├── analytics.py        # Behaviour analytics engine
├── ai_insights.py      # Claude API integration for AI coaching
├── seed_data.py        # Demo data generator
├── requirements.txt    # Python dependencies
└── productivity_data.json  # Auto-created data store
```

## AI Features (Anthropic API Key Required)

Add your API key in the sidebar or set `ANTHROPIC_API_KEY` env variable:

- **Daily Brief** — personalised analysis of today's patterns + 1 key action
- **Weekly Strategy** — data-driven coaching for the week ahead  
- **AI Chat** — interactive coach that references your actual productivity data
- **Plan Scoring** — evaluates your daily task plan against your energy patterns

## Analytics Engine

The `BehaviourAnalytics` class computes:

- **Productivity Score** (0–100) weighted across completion rate, focus hours, habits, efficiency
- **Peak Performance Hours** — identifies your highest-quality work windows from session data
- **Estimation Accuracy** — tracks time over/underruns, detects Hofstadter patterns
- **Energy-Productivity Correlation** — statistical correlation between energy logs and focus quality
- **Habit Streaks** — current/longest streaks and 30-day completion rates
- **Behavioural Pattern Detection** — auto-flags low completion, insufficient deep work, broken streaks

## Data Storage

All data is stored locally in `productivity_data.json`. Use Settings → Export to back up your data.
