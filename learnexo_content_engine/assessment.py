"""
Stage 1 — Learning Style Detector

Analyses student activity data and identifies their learning style
(visual, auditory, or kinesthetic) using the Groq LLM.

This is Stage 1 of the LearNexo pipeline. The output feeds into:
  Stage 2 → learning_path_generator.py  (POST /learning-path)
  Stage 3 → content_generator.py        (POST /content)

Usage:
  python assessment.py

Requires GROQ_API_KEY in your .env file.
"""

import os
import json
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise EnvironmentError(
        "GROQ_API_KEY is not set. Add it to your .env file.\n"
        "Get a free key at https://console.groq.com"
    )

os.environ["GROQ_API_KEY"] = GROQ_API_KEY


STAGE1_TEMPLATE = """
Analyze the student activity data and complete the following tasks:

1. Identify the student's learning style (visual, auditory, or kinesthetic).
2. Provide a 2-3 sentence explanation for your conclusion using evidence from the activity patterns.
3. Recommend two personalised content formats that match this learning style.
4. Suggest one potential risk of misclassification.

Student Activity:
{student_activity}

You MUST output your response strictly following the JSON schema below:

{format_instructions}
""".strip()


class LearningStyleEvaluation(BaseModel):
    learning_style: str = Field(..., description="One of: visual, auditory, or kinesthetic")
    explanation: str = Field(..., description="2-3 sentence reasoning")
    recommended_formats: List[str] = Field(..., description="Two recommended content formats")
    risk_of_misclassification: str = Field(..., description="One risk of misclassification")


parser = PydanticOutputParser(pydantic_object=LearningStyleEvaluation)
format_instructions = parser.get_format_instructions()

prompt = PromptTemplate(
    template=STAGE1_TEMPLATE,
    input_variables=["student_activity"],
    partial_variables={"format_instructions": format_instructions},
)

llm = ChatGroq(
    temperature=0.1,
    model="llama-3.3-70b-versatile",
)

chain = prompt | llm | parser


if __name__ == "__main__":
    input_data = {
        "student_activity": json.dumps({
            "activity": [
                "Student spends most time watching video lessons",
                "Frequently rewatches animated explainers",
                "Avoids PDFs and long text readings",
                "Highest quiz scores occur after video-based review sessions",
                "Skips audio-only resources regularly",
            ]
        }, indent=2)
    }

    filled_prompt = prompt.format(**input_data)
    print("===== FILLED PROMPT SENT TO LLM =====\n")
    print(filled_prompt)

    result = chain.invoke(input_data)

    print("\n===== PARSED MODEL OUTPUT =====\n")
    print(json.dumps(result.model_dump(), indent=4, ensure_ascii=False))

    print("\nLearning Style Identified:", result.learning_style)
    print("\nExplanation:\n", result.explanation)
    print("\nRecommended Formats:", result.recommended_formats)
    print("\nRisk of Misclassification:", result.risk_of_misclassification)
