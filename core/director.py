import os
import json
from core.schemas import LessonPlan, Scene
from core.safety import enforce_kid_safety, sanitize_theme
from core.script_agent import generate_script
from core.media_agent import generate_scene_images, generate_scene_audio, write_asset_manifest
from core.assembler import assemble
from tools.genai_client import GenAIClient
from tools.json_utils import extract_json

DIRECTOR_SYSTEM = (
    "Return ONLY valid JSON. No markdown. No backticks. No prose. "
    "You are planning a short kid-safe lesson for ages 7 to 12. "
    "No romance or sexual content, no bullying, no gore."
)

def _build_plan(genai_client, user_prompt: str, age: int, difficulty: int, duration_sec: int, theme: str) -> LessonPlan:
    theme = sanitize_theme(theme)
    enforce_kid_safety(user_prompt)
    req = {
        "age": age,
        "difficulty": difficulty,
        "duration_sec": duration_sec,
        "theme": theme,
        "user_prompt": user_prompt,
        "required_keys": ["topic", "learning_goals", "safety_rules", "scenes"],
        "rules": [
            "Return ONLY JSON.",
            "topic is a short string.",
            "learning_goals is an array of up to 3 short strings.",
            "safety_rules is an array of short strings.",
            "scenes is an array with 5 to 7 items.",
            "Each scene item must have: index (int), title (string), target_duration_sec (int 3..60).",
            "Total target_duration_sec should be close to duration_sec."
        ]
    }
    text = genai_client.generate_text(system=DIRECTOR_SYSTEM, user=json.dumps(req))
    enforce_kid_safety(text)
    data = extract_json(text)

    topic = str(data.get("topic", "Lesson")).strip()[:80] or "Lesson"
    learning_goals = data.get("learning_goals", [])
    if not isinstance(learning_goals, list):
        learning_goals = []
    learning_goals = [str(x).strip()[:120] for x in learning_goals if str(x).strip()][:3]

    safety_rules = data.get("safety_rules", [])
    if not isinstance(safety_rules, list):
        safety_rules = []
    safety_rules = [str(x).strip()[:120] for x in safety_rules if str(x).strip()][:8]

    raw_scenes = data.get("scenes", [])
    if not isinstance(raw_scenes, list) or len(raw_scenes) < 5:
        raw_scenes = [{"index": i + 1, "title": f"Scene {i+1}", "target_duration_sec": max(8, duration_sec // 6)} for i in range(6)]

    scenes = []
    base = max(6, duration_sec // max(5, min(7, len(raw_scenes))))
    for i, s in enumerate(raw_scenes[:7]):
        idx = int(s.get("index", i + 1))
        title = str(s.get("title", f"Scene {idx}")).strip()[:60] or f"Scene {idx}"
        tdur = int(s.get("target_duration_sec", base))
        tdur = max(3, min(60, tdur))
        scenes.append(Scene(index=idx, title=title, narration="", on_screen_text="", visual_prompt="", quiz_prompt=None, target_duration_sec=tdur))

    total = sum(x.target_duration_sec for x in scenes)
    if total <= 0:
        total = 1
    scale = duration_sec / total
    if scale < 0.7 or scale > 1.3:
        for s in scenes:
            s.target_duration_sec = max(3, min(60, int(round(s.target_duration_sec * scale))))

    return LessonPlan(
        age=age,
        difficulty=difficulty,
        duration_sec=duration_sec,
        theme=theme,
        topic=topic,
        learning_goals=learning_goals or ["Understand the key idea", "See a real example", "Answer a quick question"],
        safety_rules=safety_rules or ["Kid-safe language", "No romance/sexual content", "No bullying or humiliation"],
        scenes=scenes
    )

def run_pipeline(user_prompt: str, age: int, difficulty: int, duration_sec: int, theme: str, out_dir: str, gen_images: bool, gen_audio: bool, burn_subs: bool, api_key: str) -> dict:
    os.makedirs(out_dir, exist_ok=True)
    genai_client = GenAIClient(api_key=api_key)

    plan = _build_plan(genai_client, user_prompt, age, difficulty, duration_sec, theme)
    plan_dir = os.path.join(out_dir, "plan")
    script_dir = os.path.join(out_dir, "script")
    media_dir = os.path.join(out_dir, "media")
    os.makedirs(plan_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(media_dir, exist_ok=True)

    plan_path = os.path.join(plan_dir, "plan.json")
    with open(plan_path, "w", encoding="utf-8") as f:
        json.dump(plan.model_dump(), f, indent=2)

    script = generate_script(genai_client, plan)
    script_path = os.path.join(script_dir, "script.json")
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, indent=2)

    scenes = script["scenes"]
    image_paths = []
    audio_paths = []

    if gen_images:
        image_paths = generate_scene_images(genai_client, script, out_dir)
    else:
        for s in scenes:
            idx = int(s["index"])
            image_paths.append(os.path.join(out_dir, f"scene_{idx:02d}.png"))

    if gen_audio:
        audio_paths = generate_scene_audio(genai_client, script, out_dir)
    else:
        for s in scenes:
            idx = int(s["index"])
            audio_paths.append(os.path.join(out_dir, f"scene_{idx:02d}.wav"))

    assets_path = write_asset_manifest(script, image_paths, audio_paths, out_dir)
    from tools.env_utils import has_ffmpeg
    
    from tools.env_utils import has_ffmpeg

    assembled = None
    captions_srt = None
    joined_video_path = None
    final_video_path = None
    
    if has_ffmpeg():
        try:
            assembled = assemble(out_dir, script, assets_path, burn_subs)
            captions_srt = assembled.get("captions_srt")
            joined_video_path = assembled.get("joined_video")
            final_video_path = assembled.get("final_video")
        except Exception:
            assembled = None
    
    result = {
        "plan": plan.model_dump(),
        "script": script,
        "assets_path": assets_path,
        "captions_srt": captions_srt,
        "joined_video_path": joined_video_path,
        "final_video_path": final_video_path
    }
    
    result_path = os.path.join(out_dir, "result.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result
