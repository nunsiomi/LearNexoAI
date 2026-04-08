from typing import List, Literal
from pydantic import BaseModel, Field

LearningStyleLiteral = Literal["visual", "auditory", "kinesthetic"]

class StudentActivity(BaseModel):
    activity: List[str] = Field(..., min_length=1)

class LearningStyleRequest(BaseModel):
    student_activity: StudentActivity

class LearningStyleEvaluation(BaseModel):
    learning_style: LearningStyleLiteral
    explanation: str
    recommended_formats: List[str]
    risk_of_misclassification: str

class LearningStyleResponse(BaseModel):
    learning_style: LearningStyleLiteral