import json

from app.core.config import GROQ_API_KEY, GROQ_MODEL
from app.schemas.learning_style import StudentActivity
from app.services.learning_style_service import LearningStyleService


def run_sample_assessment() -> dict:
    service = LearningStyleService(
        groq_api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
    )

    student_activity = StudentActivity(
        activity=[
            "Student spends most time watching video lessons",
            "Frequently rewatches animated explainers",
            "Avoids PDFs and long text readings",
            "Highest quiz scores occur after video-based review sessions",
            "Skips audio-only resources regularly",
        ]
    )

    result = service.evaluate(student_activity)
    return result.model_dump()


def main() -> None:
    result = run_sample_assessment()
    print(json.dumps(result, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()