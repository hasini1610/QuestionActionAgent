import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing.")

client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.1-flash-lite"


def clean_json(text):
    """Clean Gemini response and convert it into JSON."""

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start:end + 1])

        raise ValueError("Gemini returned invalid JSON.")


def generate_plan(question):
    prompt = f"""
You are Question → Action Agent.

Your job is NOT simply to answer the user's question.

Instead, understand what the user wants to achieve and convert their
question into a practical, personalized and prioritized action plan.

Follow this process:

1. Understand the user's intent.
2. Identify the main goal.
3. Identify constraints such as time, skill level and deadline.
4. Make reasonable assumptions if information is missing.
5. Break the goal into actionable steps.
6. Prioritize the steps.
7. Create a realistic timeline.
8. Give actions the user can start today.
9. Give a measurable success checkpoint.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "goal": "main goal",
  "assumptions": [
    "assumption 1",
    "assumption 2"
  ],
  "priorities": [
    "priority 1",
    "priority 2",
    "priority 3"
  ],
  "action_plan": [
    {{
      "phase": "Phase 1",
      "duration": "Week 1",
      "tasks": [
        "task 1",
        "task 2"
      ]
    }}
  ],
  "today_actions": [
    "action 1",
    "action 2",
    "action 3"
  ],
  "success_checkpoint": "measurable checkpoint"
}}

User question:

{question}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return clean_json(response.text)


def replan(progress):
    prompt = f"""
You are the adaptive planning component of Question → Action Agent.

The user already has a plan and has now reported their progress.

Analyze their progress and intelligently adjust the plan.

Do not simply repeat the old plan.

If they completed tasks, move forward.

If they struggled, reduce difficulty, change the sequence or add
practice.

If they are ahead, increase the challenge appropriately.

Return ONLY valid JSON.

Use exactly this structure:

{{
  "goal": "string",
  "progress_summary": "string",
  "completed": [
    "string"
  ],
  "struggling_with": [
    "string"
  ],
  "adjustments": [
    "string"
  ],
  "updated_plan": [
    "string"
  ],
  "today_actions": [
    "string"
  ],
  "next_checkpoint": "string"
}}

User progress:

{progress}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return clean_json(response.text)
