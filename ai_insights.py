import anthropic
import json
from typing import Optional


class AIInsightsEngine:
    """Uses Claude API to generate personalised behavioural coaching."""

    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def generate_daily_brief(self, analytics_data: dict, user_name: str = "User") -> str:
        prompt = f"""You are a world-class productivity coach and behavioural scientist.
Analyse this user's productivity data and provide a sharp, personalised daily brief.

DATA:
{json.dumps(analytics_data, indent=2)}

Write a concise daily brief (4-6 sentences) that:
1. Acknowledges their current productivity score and trend
2. Identifies the single most impactful pattern (positive or negative)
3. Gives ONE specific, actionable recommendation for today
4. Ends with a motivating but realistic statement

Be direct, data-driven, and human. Avoid generic advice. Reference specific numbers from the data.
Format: Plain paragraphs, no bullet points or headers."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def analyse_behaviour_pattern(self, pattern_data: dict, context: str = "") -> str:
        prompt = f"""You are a behavioural intelligence system analysing productivity patterns.

DETECTED PATTERN:
{json.dumps(pattern_data, indent=2)}

CONTEXT: {context}

Provide a deep analysis (3-4 sentences) that:
1. Explains WHY this pattern is occurring (root cause, not surface symptoms)
2. Shows the downstream consequences if uncorrected
3. Gives a specific evidence-based intervention strategy

Be precise and scientific. Reference psychology/neuroscience principles where relevant.
Tone: expert colleague, not generic chatbot."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def generate_weekly_strategy(self, weekly_data: dict) -> str:
        prompt = f"""You are a strategic productivity advisor reviewing a week of behavioural data.

WEEKLY DATA:
{json.dumps(weekly_data, indent=2)}

Generate a focused weekly strategy (5-7 sentences) that:
1. Summarises what this week's data reveals about the user's work style
2. Identifies their top strength to double down on
3. Pinpoints the single biggest bottleneck to eliminate
4. Recommends 2 specific tactics for next week (time-blocking, habit changes, etc.)
5. Sets a realistic but ambitious target score for next week

Be honest about weaknesses. Ground advice in the actual data. Write as a trusted advisor."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    def chat_with_coach(self, conversation_history: list, user_data: dict) -> str:
        system = f"""You are an expert productivity coach and behavioural scientist embedded in a 
Productivity Optimizer app. You have access to the user's real-time data:

{json.dumps(user_data, indent=2)}

Your role:
- Answer questions about their productivity patterns
- Give evidence-based, personalised advice
- Reference their actual data in responses
- Be direct, insightful, and motivating without being generic

Keep responses concise (2-4 sentences) unless detail is specifically requested."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=400,
            system=system,
            messages=conversation_history
        )
        return response.content[0].text

    def score_daily_plan(self, planned_tasks: list, energy_logs: list) -> str:
        prompt = f"""Evaluate this person's daily task plan against their energy patterns.

PLANNED TASKS (with priorities and time estimates):
{json.dumps(planned_tasks, indent=2)}

HISTORICAL ENERGY PATTERNS:
{json.dumps(energy_logs, indent=2)}

Score this plan (1-10) and explain:
1. Is high-priority work scheduled during peak energy?
2. Is the total load realistic?
3. What's the biggest scheduling mistake?
4. Suggest 1 rearrangement that would improve the plan

Be specific and numerical. Mention exact tasks by name."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text
