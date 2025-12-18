import json
from core.schemas import LessonPlan
from core.safety import enforce_kid_safety
from tools.json_utils import extract_json

SCRIPT_SYSTEM = (
    "Return ONLY valid JSON. No markdown. No backticks. No prose. "
    "You write short educational scripts for kids aged 7 to 12. "
    "Always child-safe, positive, age-appropriate. "
    "No romance or sexual content, no bullying, no humiliation, no gore. "
    "Output must be an object with key 'scenes' only."
)

def generate_script(genai_client, plan: LessonPlan) -> dict:
    plan_json = plan.model_dump()
    enforce_kid_safety(json.dumps(plan_json))
    user_msg = {
        "plan": plan_json,
        "rules": [
            "Return ONLY JSON.",
            "Top-level keys: scenes only.",
            "scenes must be an array of 5 to 7 items.",
            "Each scene must include: index, title, narration, on_screen_text, visual_prompt, quiz_prompt (nullable), target_duration_sec.",
            "on_screen_text must be under 8 words.",
            "Add 1 or 2 quiz_prompt values across the whole lesson.",
            "Keep language appropriate for the given age."
        ]
    }
    text = genai_client.generate_text(system=SCRIPT_SYSTEM, user=json.dumps(user_msg))
    enforce_kid_safety(text)
    data = extract_json(text)
    if "scenes" not in data or not isinstance(data["scenes"], list):
        raise ValueError("Bad script JSON")
    return data
