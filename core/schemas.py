from typing import List, Optional
from pydantic import BaseModel, Field

class Scene(BaseModel):
    index: int
    title: str
    narration: str
    on_screen_text: str
    visual_prompt: str
    quiz_prompt: Optional[str] = None
    target_duration_sec: int = Field(ge=3, le=60)

class LessonPlan(BaseModel):
    age: int = Field(ge=7, le=12)
    difficulty: int = Field(ge=1, le=5)
    duration_sec: int = Field(ge=30, le=180)
    theme: str
    topic: str
    learning_goals: List[str]
    safety_rules: List[str]
    scenes: List[Scene]
