import json
from core.schemas import LessonPlan
from core.safety import enforce_kid_safety

SCRIPT_SYSTEM = (
    "You write short educational scripts for kids aged 7 to 12. "
    "Always be child-safe, positive, and age-appropriate. "
    "No romance or sexual content, no bullying, no humiliation, no gore. "
    "Write scene-based output as strict JSON matching the provided schema. "
    "Use simple words for the given age. Keep on_screen_text under 8 words. "
    "Add 1 or 2 quiz prompts across the whole lesson. "
    "Keep total duration close to the requested duration."
)

def generate_script(genai_client, plan: LessonPlan) -> dict:
    plan_json = plan.model_dump()
    enforce_kid_safety(json.dumps(plan_json))
    schema_hint = {
        "scenes": [
            {
                "index": 1,
                "title": "string",
                "narration": "string",
                "on_screen_text": "string",
                "visual_prompt": "string",
                "quiz_prompt": "string or null",
                "target_duration_sec": 10
            }
        ]
    }
    user_msg = {
        "plan": plan_json,
        "output_schema_example": schema_hint,
        "output_rules": [
            "Return ONLY JSON. No extra keys at top-level except 'scenes'.",
            "Total scenes between 5 and 7.",
            "Total target_duration_sec must be close to plan.duration_sec.",
            "Use the theme strongly in visuals and narration.",
            "Keep narration friendly and short per scene."
        ]
    }
    text = genai_client.generate_text(system=SCRIPT_SYSTEM, user=json.dumps(user_msg))
    enforce_kid_safety(text)
    data = json.loads(text)
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("Bad script JSON")
    return data
