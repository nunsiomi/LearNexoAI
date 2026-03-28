"""
Stage 3 — Learning Content Generator

Takes a topic + learning style + subject + class level and generates
fully tailored learning content in the format that best matches the
student's learning style (visual, auditory, or kinesthetic).

For visual learners, YouTube videos are automatically fetched and
attached to the response using the YouTube Data API v3.
"""

import os
from models import ContentRequest, ContentResponse
from prompts import get_content_prompt, content_parser
from llm_config import llm_creative


def generate_content(request: ContentRequest) -> ContentResponse:
    """
    Generate personalized learning content for a specific topic,
    tailored to the student's learning style.

    The content type returned depends on the learning style:
      - visual      → visual_content populated (+ YouTube videos if API key set); others null
      - auditory    → auditory_content populated; others null
      - kinesthetic → kinesthetic_content populated; others null

    Args:
        request: ContentRequest with learning_style, topic, subject,
                 class_level, content_depth, and optional student_id.

    Returns:
        ContentResponse with style-specific content, assessment questions,
        summary, and study tips.
    """
    prompt = get_content_prompt(request.learning_style)
    chain = prompt | llm_creative | content_parser

    raw = chain.invoke(
        {
            "subject": request.subject,
            "class_level": request.class_level,
            "topic": request.topic,
            "content_depth": request.content_depth,
        }
    )

    # Attach student metadata from the request
    raw.student_id = request.student_id
    raw.learning_style = request.learning_style
    raw.subject = request.subject
    raw.class_level = request.class_level
    raw.topic = request.topic
    raw.content_depth = request.content_depth

    # ── YouTube integration for visual learners ──────────────────────────────
    if request.learning_style == "visual" and raw.visual_content is not None:
        youtube_api_key = os.environ.get("YOUTUBE_API_KEY")
        if youtube_api_key:
            try:
                from youtube_recommender import recommend_videos
                recommendation = recommend_videos(
                    topic=request.topic,
                    subject=request.subject,
                    class_level=request.class_level,
                    max_results=5,
                )
                # Attach as list of dicts so it serialises cleanly via Pydantic
                raw.visual_content.youtube_videos = [
                    v.model_dump() for v in recommendation.videos
                ]
            except Exception as e:
                # Never let YouTube failure block the main content response
                raw.visual_content.youtube_videos = []
        else:
            raw.visual_content.youtube_videos = None

    return raw
