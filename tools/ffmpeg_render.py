import os
import subprocess
import shlex

def _run(cmd: str):
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(p.stderr.strip() or p.stdout.strip() or "ffmpeg error")

def render_scene_video(image_path: str, audio_path: str, duration_sec: int, out_path: str):
    fps = 30
    frames = max(1, int(duration_sec * fps))
    vf = f"scale=1280:720,zoompan=z='min(zoom+0.0008,1.12)':d={frames}:s=1280x720:fps={fps}"
    cmd = (
        f"ffmpeg -y -hide_banner -loglevel error "
        f"-loop 1 -t {duration_sec} -i {shlex.quote(image_path)} "
        f"-i {shlex.quote(audio_path)} "
        f"-vf {shlex.quote(vf)} -r {fps} "
        f"-c:v libx264 -pix_fmt yuv420p -c:a aac -shortest "
        f"{shlex.quote(out_path)}"
    )
    _run(cmd)

def concat_videos(video_paths: list, out_path: str):
    base = os.path.dirname(out_path)
    lst = os.path.join(base, "concat_list.txt")
    with open(lst, "w", encoding="utf-8") as f:
        for p in video_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
    cmd = (
        f"ffmpeg -y -hide_banner -loglevel error "
        f"-f concat -safe 0 -i {shlex.quote(lst)} "
        f"-c copy {shlex.quote(out_path)}"
    )
    _run(cmd)

def burn_subtitles(video_in: str, srt_path: str, video_out: str):
    vf = f"subtitles={srt_path}"
    cmd = (
        f"ffmpeg -y -hide_banner -loglevel error "
        f"-i {shlex.quote(video_in)} "
        f"-vf {shlex.quote(vf)} "
        f"-c:a copy {shlex.quote(video_out)}"
    )
    _run(cmd)
