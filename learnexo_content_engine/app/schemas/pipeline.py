from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.learning_style import StudentActivity, LearningStyleLiteral

class GenerateLearningRequest(BaseModel):
    student_activity: StudentActivity
    subject: str = Field(..., min_length=2)
    class_level: str = Field(..., min_length=2)
    term: str = "First"
    student_id: Optional[str] = None
    content_depth: str = "core"
    generate_content_for_first_topic: bool = True

class GenerateLearningResponse(BaseModel):
    learning_style: LearningStyleLiteral
    curriculum: dict
    content: Optional[dict] = None