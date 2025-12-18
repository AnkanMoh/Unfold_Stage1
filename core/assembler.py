import os
import json
from tools.subtitles import build_srt
from tools.ffmpeg_render import render_scene_video, concat_videos, burn_subtitles

def assemble(out_dir: str, script: dict, assets_path: str, burn_subs: bool) -> dict:
    with open(assets_path, "r", encoding="utf-8") as f:
        assets = json.load(f)

    srt_path = os.path.join(out_dir, "captions.srt")
    build_srt(script, srt_path)

    scene_videos = []
    for s in assets["scenes"]:
        idx = int(s["index"])
        img = s["image_path"]
        aud = s["audio_path"]
        dur = int(s.get("target_duration_sec", 10))
        out_mp4 = os.path.join(out_dir, f"scene_{idx:02d}.mp4")
        render_scene_video(image_path=img, audio_path=aud, duration_sec=dur, out_path=out_mp4)
        scene_videos.append(out_mp4)

    joined = os.path.join(out_dir, "joined.mp4")
    concat_videos(scene_videos, joined)

    final_path = os.path.join(out_dir, "final.mp4")
    if burn_subs:
        burn_subtitles(video_in=joined, srt_path=srt_path, video_out=final_path)
    else:
        final_path = joined

    return {
        "captions_srt": srt_path,
        "joined_video": joined,
        "final_video": final_path
    }
