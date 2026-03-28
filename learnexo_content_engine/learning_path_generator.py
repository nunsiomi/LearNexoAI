"""
Stage 2 — Learning Path Generator

Takes a student's determined learning style + subject + class level
and generates a full, Nigerian-curriculum-aligned learning path.
"""

from typing import Optional
from langchain_core.output_parsers import PydanticOutputParser

from models import LearningPathRequest, LearningPathResponse
from prompts import learning_path_prompt, learning_path_parser
from llm_config import llm_structured


def generate_learning_path(request: LearningPathRequest) -> LearningPathResponse:
    """
    Generate a personalized learning path for a Nigerian secondary school student.

    Args:
        request: LearningPathRequest containing learning_style, subject,
                 class_level, term, and optional student_id.

    Returns:
        LearningPathResponse with ordered topics, durations, formats, and exam tips.

    Example:
        >>> from models import LearningPathRequest
        >>> req = LearningPathRequest(
        ...     learning_style="visual",
        ...     subject="Mathematics",
        ...     class_level="SS2",
        ...     term="First",
        ...     student_id="stu_001"
        ... )
        >>> path = generate_learning_path(req)
        >>> print(path.total_topics, "topics generated")
    """
    chain = learning_path_prompt | llm_structured | learning_path_parser

    raw = chain.invoke(
        {
            "learning_style": request.learning_style,
            "subject": request.subject,
            "class_level": request.class_level,
            "term": request.term or "First",
        }
    )

    # Attach student metadata from the request
    raw.student_id = request.student_id
    raw.learning_style = request.learning_style
    raw.subject = request.subject
    raw.class_level = request.class_level
    raw.term = request.term or "First"

    return raw
