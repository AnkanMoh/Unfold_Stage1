import base64
from google import genai

class GenAIClient:
    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def generate_text(self, system: str, user: str, model: str = "gemini-2.5-flash"):
        resp = self.client.models.generate_content(
            model=model,
            contents=[{"role": "user", "parts": [{"text": f"System:\n{system}\n\nUser:\n{user}"}]}]
        )
        text = getattr(resp, "text", None)
        if not text:
            raise RuntimeError("No text returned")
        return text.strip()

    def generate_image(self, prompt: str, model: str = "imagen-3.0-generate-002"):
        resp = self.client.models.generate_images(model=model, prompt=prompt)
        images = getattr(resp, "generated_images", None)
        if not images:
            raise RuntimeError("No image returned")
        return images[0].image.image_bytes

    def generate_audio(self, text: str):
        resp = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[{"role": "user", "parts": [{"text": f"Generate speech audio for this kid-safe narration:\n{text}"}]}]
        )
        cand = resp.candidates[0]
        parts = cand.content.parts
        for p in parts:
            if hasattr(p, "inline_data") and p.inline_data and getattr(p.inline_data, "data", None):
                data = p.inline_data.data
                try:
                    return base64.b64decode(data)
                except Exception:
                    return None
        return None
