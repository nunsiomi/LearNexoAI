from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.services.learning_style_service import LearningStyleService

def get_learning_style_service() -> LearningStyleService:
    return LearningStyleService(
        groq_api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
    )