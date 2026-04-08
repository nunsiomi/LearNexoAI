from typing import Any, Literal

from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from app.core.config import GROQ_API_KEY, GROQ_MODEL

LearningStyle = Literal["visual", "auditory", "kinesthetic"]
ClassLevel = Literal["JSS1", "JSS2", "JSS3", "SS1", "SS2", "SS3"]
TermName = Literal["First", "Second", "Third"]


class LearningPathOutput(BaseModel):
    subject: str = Field(..., description="Subject name")
    class_level: str = Field(..., description="Student class level")
    term: str = Field(..., description="Academic term")
    learning_style: str = Field(..., description="visual, auditory, or kinesthetic")
    recommended_content_format: list[str] = Field(
        ...,
        description="Best content formats for the student's learning style",
    )
    study_strategy: str = Field(
        ...,
        description="Overall study strategy tailored to the learning style",
    )
    exam_tips: list[str] = Field(
        ...,
        description="WAEC/NECO/JAMB-focused tips for the subject",
    )
    topics: list[dict[str, Any]] = Field(
        ...,
        description=(
            "Ordered list of topics. Each topic should include topic, subtopics, "
            "learning_objectives, estimated_duration_hours, prerequisites, and exam_relevance."
        ),
    )


LEARNING_PATH_TEMPLATE = """
You are an expert Nigerian curriculum planner for secondary school students.

Your task is to generate a personalised learning path for a student using:
- learning style
- subject
- class level
- academic term

The learning path must:
1. Follow Nigerian secondary school expectations and exam relevance for WAEC, NECO, and JAMB where appropriate.
2. Be realistic for the student's class level.
3. Be tailored to the student's learning style.
4. Return an ordered list of topics for the term.
5. Include:
   - subtopics
   - learning objectives
   - estimated duration in hours
   - prerequisites
   - exam relevance
6. Include recommended content formats for the student's learning style.
7. Include an overall study strategy.
8. Include subject-specific exam tips.

Learning style: {learning_style}
Subject: {subject}
Class level: {class_level}
Term: {term}
Student ID: {student_id}

Learning style guidance:
- visual: prefer diagrams, structured notes, concept maps, charts, color-coded summaries
- auditory: prefer explanations, narration scripts, discussion prompts, mnemonics, spoken summaries
- kinesthetic: prefer hands-on exercises, practical activities, experiments, interactive tasks

Important constraints:
- Use Nigerian context where useful.
- Keep topic ordering logical.
- Be concise but informative.
- Return valid JSON only.
- Use the schema exactly as required.

{format_instructions}
""".strip()


class LearningPathService:
    def __init__(
        self,
        groq_api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.parser = JsonOutputParser(pydantic_object=LearningPathOutput)
        self.prompt = PromptTemplate(
            template=LEARNING_PATH_TEMPLATE,
            input_variables=[
                "learning_style",
                "subject",
                "class_level",
                "term",
                "student_id",
            ],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.llm = ChatGroq(
            api_key=groq_api_key or GROQ_API_KEY,
            model=model or GROQ_MODEL,
            temperature=0.2,
        )
        self.chain = self.prompt | self.llm | self.parser

    def generate(
        self,
        learning_style: LearningStyle,
        subject: str,
        class_level: ClassLevel,
        student_id: str | None = None,
        term: TermName = "First",
    ) -> dict[str, Any]:
        subject = subject.strip()
        if not subject:
            raise ValueError("subject cannot be empty")

        result = self.chain.invoke(
            {
                "learning_style": learning_style,
                "subject": subject,
                "class_level": class_level,
                "term": term,
                "student_id": student_id or "N/A",
            }
        )

        if not isinstance(result, dict):
            raise ValueError("Invalid learning path response format")

        result.setdefault("subject", subject)
        result.setdefault("class_level", class_level)
        result.setdefault("term", term)
        result.setdefault("learning_style", learning_style)
        result.setdefault("recommended_content_format", [])
        result.setdefault("study_strategy", "")
        result.setdefault("exam_tips", [])
        result.setdefault("topics", [])

        return result