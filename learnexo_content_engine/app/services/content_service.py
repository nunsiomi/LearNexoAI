from __future__ import annotations

import os
from typing import Any, Literal, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

LearningStyle = Literal["visual", "auditory", "kinesthetic"]
ClassLevel = Literal["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]
ContentDepth = Literal["introduction", "core", "advanced", "revision"]


class VisualContentBlock(BaseModel):
    concept_map: str = Field(..., description="Concept map or mind map description")
    diagram_descriptions: list[str] = Field(
        ...,
        description="Descriptions of useful diagrams or illustrations"
    )
    infographic_outline: list[str] = Field(
        ...,
        description="Infographic sections or outline"
    )
    colour_coded_summary: list[str] = Field(
        ...,
        description="Colour-coded or grouped summary points"
    )
    step_by_step_visual_guide: list[str] = Field(
        ...,
        description="Step-by-step visual guide"
    )
    youtube_videos: list[dict[str, Any]] | None = Field(
        default=None,
        description="Optional YouTube recommendations for visual learners"
    )


class AuditoryContentBlock(BaseModel):
    narration_script: str = Field(..., description="Audio-style lesson narration")
    storytelling_narrative: str = Field(
        ...,
        description="Nigerian context story that explains the concept"
    )
    mnemonics: list[str] = Field(..., description="Memory aids, rhymes, or mnemonics")
    discussion_questions: list[str] = Field(
        ...,
        description="Oral discussion questions"
    )
    podcast_style_qa: list[dict[str, str]] = Field(
        ...,
        description="Question-answer pairs in spoken style"
    )
    spoken_key_points: list[str] = Field(
        ...,
        description="Key points as they would be spoken aloud"
    )


class KinestheticContentBlock(BaseModel):
    hands_on_activities: list[str] = Field(
        ...,
        description="Hands-on activities doable at home or in class"
    )
    simple_experiments: list[str] = Field(
        ...,
        description="Simple experiments using common materials"
    )
    practical_guide: list[str] = Field(
        ...,
        description="Step-by-step practical guide"
    )
    real_world_applications: list[str] = Field(
        ...,
        description="Applications in Nigerian daily life"
    )
    interactive_exercises: list[str] = Field(
        ...,
        description="Interactive or action-based exercises"
    )
    collaborative_activities: list[str] = Field(
        ...,
        description="Group or peer activities"
    )


class ContentOutput(BaseModel):
    topic: str
    subject: str
    class_level: str
    learning_style: str
    content_depth: str

    learning_objectives: list[str]
    key_concepts: list[str]

    visual_content: VisualContentBlock | None = None
    auditory_content: AuditoryContentBlock | None = None
    kinesthetic_content: KinestheticContentBlock | None = None

    assessment_questions: dict[str, list[str]]
    key_points_summary: list[str]
    study_tips_for_style: list[str]
    next_topic_preview: str


CONTENT_TEMPLATE = """
You are an expert Nigerian secondary-school lesson designer.

Generate complete lesson content for this student and topic.

INPUT
- Learning style: {learning_style}
- Topic: {topic}
- Subject: {subject}
- Class level: {class_level}
- Content depth: {content_depth}
- Student ID: {student_id}
- Curriculum context: {generated_curriculum}

REQUIREMENTS
1. Align the content to Nigerian secondary school learning context.
2. Use everyday Nigerian examples where useful: Naira, Lagos, Abuja, Kano, markets, transport, food, local school settings, daily life.
3. Keep the content suitable for the given class level.
4. Make the lesson style-specific:
   - visual: concept maps, diagram descriptions, infographic outline, colour-coded summary, visual steps
   - auditory: narration script, story-based explanation, mnemonics, discussion prompts, spoken Q&A
   - kinesthetic: hands-on activities, simple experiments, practical guide, real-world tasks, collaborative activities
5. Return:
   - learning objectives
   - key concepts
   - exactly one populated style-specific content block
   - assessment questions:
       * multiple_choice
       * short_answer
       * theory
   - key points summary
   - study tips for this learning style
   - next topic preview
6. If curriculum context is provided, make the lesson consistent with it and choose a reasonable next topic from that context when possible.
7. Return valid JSON only.
8. Follow the schema exactly.

{format_instructions}
""".strip()


class ContentService:
    def __init__(
        self,
        groq_api_key: Optional[str] = None,
        model: Optional[str] = None,
    ) -> None:
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        self.model = model or os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not self.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set")

        self.parser = JsonOutputParser(pydantic_object=ContentOutput)
        self.prompt = PromptTemplate(
            template=CONTENT_TEMPLATE,
            input_variables=[
                "learning_style",
                "topic",
                "subject",
                "class_level",
                "content_depth",
                "student_id",
                "generated_curriculum",
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.llm = ChatGroq(
            api_key=self.groq_api_key,
            model=self.model,
            temperature=0.2,
        )
        self.chain = self.prompt | self.llm | self.parser

    def _attach_youtube_if_needed(
        self,
        result: dict[str, Any],
        learning_style: LearningStyle,
        topic: str,
        subject: str,
        class_level: ClassLevel,
    ) -> dict[str, Any]:
        if learning_style != "visual":
            return result

        youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        if not youtube_api_key:
            # README says content generation should still work and videos can be null
            visual_block = result.get("visual_content") or {}
            visual_block["youtube_videos"] = None
            result["visual_content"] = visual_block
            return result

        try:
            # Optional integration if your old flat module still exists
            from youtube_recommender import recommend_youtube_videos  # type: ignore

            videos = recommend_youtube_videos(
                topic=topic,
                subject=subject,
                class_level=class_level,
                max_results=5,
            )
            visual_block = result.get("visual_content") or {}
            visual_block["youtube_videos"] = videos
            result["visual_content"] = visual_block
            return result
        except Exception:
            visual_block = result.get("visual_content") or {}
            visual_block["youtube_videos"] = None
            result["visual_content"] = visual_block
            return result

    def _normalize_result(
        self,
        result: dict[str, Any],
        topic: str,
        subject: str,
        class_level: ClassLevel,
        learning_style: LearningStyle,
        content_depth: ContentDepth,
    ) -> dict[str, Any]:
        result.setdefault("topic", topic)
        result.setdefault("subject", subject)
        result.setdefault("class_level", class_level)
        result.setdefault("learning_style", learning_style)
        result.setdefault("content_depth", content_depth)
        result.setdefault("learning_objectives", [])
        result.setdefault("key_concepts", [])
        result.setdefault("assessment_questions", {
            "multiple_choice": [],
            "short_answer": [],
            "theory": [],
        })
        result.setdefault("key_points_summary", [])
        result.setdefault("study_tips_for_style", [])
        result.setdefault("next_topic_preview", "")

        # Ensure only one style block is populated
        if learning_style == "visual":
            result.setdefault("visual_content", {
                "concept_map": "",
                "diagram_descriptions": [],
                "infographic_outline": [],
                "colour_coded_summary": [],
                "step_by_step_visual_guide": [],
                "youtube_videos": None,
            })
            result["auditory_content"] = None
            result["kinesthetic_content"] = None

        elif learning_style == "auditory":
            result.setdefault("auditory_content", {
                "narration_script": "",
                "storytelling_narrative": "",
                "mnemonics": [],
                "discussion_questions": [],
                "podcast_style_qa": [],
                "spoken_key_points": [],
            })
            result["visual_content"] = None
            result["kinesthetic_content"] = None

        elif learning_style == "kinesthetic":
            result.setdefault("kinesthetic_content", {
                "hands_on_activities": [],
                "simple_experiments": [],
                "practical_guide": [],
                "real_world_applications": [],
                "interactive_exercises": [],
                "collaborative_activities": [],
            })
            result["visual_content"] = None
            result["auditory_content"] = None

        return result

    def generate(
        self,
        topic: str,
        subject: str,
        class_level: ClassLevel,
        learning_style: LearningStyle,
        generated_curriculum: Optional[dict[str, Any]] = None,
        student_id: Optional[str] = None,
        content_depth: ContentDepth = "core",
    ) -> dict[str, Any]:
        topic = topic.strip()
        subject = subject.strip()

        if not topic:
            raise ValueError("topic cannot be empty")
        if not subject:
            raise ValueError("subject cannot be empty")

        result = self.chain.invoke(
            {
                "learning_style": learning_style,
                "topic": topic,
                "subject": subject,
                "class_level": class_level,
                "content_depth": content_depth,
                "student_id": student_id or "N/A",
                "generated_curriculum": generated_curriculum or {},
            }
        )

        if not isinstance(result, dict):
            raise ValueError("Invalid content response format")

        result = self._normalize_result(
            result=result,
            topic=topic,
            subject=subject,
            class_level=class_level,
            learning_style=learning_style,
            content_depth=content_depth,
        )

        result = self._attach_youtube_if_needed(
            result=result,
            learning_style=learning_style,
            topic=topic,
            subject=subject,
            class_level=class_level,
        )

        return result