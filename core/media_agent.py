import os
import json
import wave
import struct
from core.safety import enforce_kid_safety
from tools.placeholders import solid_png

IMAGE_STYLE = (
    "Kid-friendly colorful 2D cartoon style, clean outlines, simple shapes, "
    "safe and wholesome, no scary imagery, no weapons violence, no romance."
)

def _write_silence_wav(path: str, duration_sec: float, sample_rate: int = 22050):
    nframes = int(duration_sec * sample_rate)
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        silence = struct.pack("<h", 0)
        wf.writeframes(silence * nframes)

def generate_scene_images(genai_client, script: dict, out_dir: str) -> list:
    scenes = script["scenes"]
    paths = []
    for s in scenes:
        idx = int(s["index"])
        prompt = f"{IMAGE_STYLE}\nTheme: {s.get('title','')}\nScene: {s.get('visual_prompt','')}"
        enforce_kid_safety(prompt)
        p = os.path.join(out_dir, f"scene_{idx:02d}.png")
        img_bytes = None
        try:
            img_bytes = genai_client.generate_image(prompt=prompt)
        except Exception:
            img_bytes = solid_png()
        with open(p, "wb") as f:
            f.write(img_bytes)
        paths.append(p)
    return paths

def generate_scene_audio(genai_client, script: dict, out_dir: str) -> list:
    scenes = script["scenes"]
    paths = []
    for s in scenes:
        idx = int(s["index"])
        narration = s.get("narration", "")
        enforce_kid_safety(narration)
        p = os.path.join(out_dir, f"scene_{idx:02d}.wav")
        duration = float(s.get("target_duration_sec", 10))
        audio_bytes = None
        try:
            audio_bytes = genai_client.generate_audio(text=narration)
        except Exception:
            audio_bytes = None
        if audio_bytes:
            with open(p, "wb") as f:
                f.write(audio_bytes)
        else:
            _write_silence_wav(p, duration_sec=duration)
        paths.append(p)
    return paths

def write_asset_manifest(script: dict, image_paths: list, audio_paths: list, out_dir: str) -> str:
    scenes = script["scenes"]
    manifest = []
    for i, s in enumerate(scenes):
        idx = int(s["index"])
        manifest.append({
            "index": idx,
            "image_path": image_paths[i] if i < len(image_paths) else None,
            "audio_path": audio_paths[i] if i < len(audio_paths) else None,
            "target_duration_sec": int(s.get("target_duration_sec", 10))
        })
    path = os.path.join(out_dir, "assets.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"scenes": manifest}, f, indent=2)
    return path
