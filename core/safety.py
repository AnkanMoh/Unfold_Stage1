def enforce_kid_safety(text: str) -> None:
    t = (text or "").lower()
    blocked = [
        "sex", "sexy", "nude", "naked", "porn", "hookup", "blowjob", "handjob",
        "rape", "molest", "groom", "tease 8 year old", "past tease", "past tease 8"
    ]
    for b in blocked:
        if b in t:
            raise ValueError("Unsafe content detected")

def sanitize_theme(theme: str) -> str:
    theme = (theme or "").strip()
    if not theme:
        return "Superheroes"
    return theme[:40]
