import os
import json
import uuid
import streamlit as st
from dotenv import load_dotenv
from core.director import run_pipeline

load_dotenv()

st.set_page_config(page_title="Stage 1 Lesson Builder", layout="wide")

st.title("Stage 1: Kids Lesson Video (Storyboard)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.slider("Age", 7, 12, 8)
with col2:
    difficulty = st.slider("Difficulty", 1, 5, 3)
with col3:
    duration = st.slider("Duration (seconds)", 30, 180, 90, step=10)
with col4:
    theme = st.selectbox("Theme", ["Superheroes", "Cartoon", "Sports", "Space", "Animals", "Adventure", "Pirates", "Robots"])

prompt = st.text_area("Prompt", value="Teach triangles to an 8 year old in a super heroes way", height=120)

mode_col1, mode_col2, mode_col3 = st.columns(3)
with mode_col1:
    gen_images = st.checkbox("Generate images", value=True)
with mode_col2:
    gen_audio = st.checkbox("Generate audio", value=True)
with mode_col3:
    burn_subs = st.checkbox("Burn subtitles", value=True)

if st.button("Generate"):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        st.error("Missing GEMINI_API_KEY. Add it to your .env file.")
        st.stop()

    run_id = str(uuid.uuid4())[:8]
    out_dir = os.path.join("outputs", f"run_{run_id}")
    os.makedirs(out_dir, exist_ok=True)

    with st.spinner("Building lesson..."):
        result = run_pipeline(
            user_prompt=prompt,
            age=age,
            difficulty=difficulty,
            duration_sec=duration,
            theme=theme,
            out_dir=out_dir,
            gen_images=gen_images,
            gen_audio=gen_audio,
            burn_subs=burn_subs,
            api_key=api_key
        )

    st.success("Done")

    st.subheader("Plan")
    st.code(json.dumps(result["plan"], indent=2), language="json")

    st.subheader("Script")
    st.code(json.dumps(result["script"], indent=2), language="json")

    st.subheader("Artifacts")
    st.write(f"Output folder: {out_dir}")
    if result.get("final_video_path") and os.path.exists(result["final_video_path"]):
        st.video(result["final_video_path"])
    else:
        st.warning("Final video not found. Check FFmpeg installation and logs in the output folder.")
