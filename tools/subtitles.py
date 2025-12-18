def _fmt_time(t: float) -> str:
    if t < 0:
        t = 0
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def build_srt(script: dict, out_path: str):
    scenes = script["scenes"]
    t = 0.0
    lines = []
    idx = 1
    for s in scenes:
        dur = float(s.get("target_duration_sec", 10))
        start = t
        end = t + dur
        text = (s.get("narration", "") or "").strip().replace("\n", " ").strip()
        if not text:
            text = (s.get("on_screen_text", "") or "").strip()
        if not text:
            text = " "
        lines.append(str(idx))
        lines.append(f"{_fmt_time(start)} --> {_fmt_time(end)}")
        lines.append(text)
        lines.append("")
        idx += 1
        t = end
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
