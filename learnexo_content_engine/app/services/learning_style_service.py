from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_groq import ChatGroq

from app.schemas.learning_style import StudentActivity, LearningStyleEvaluation

STAGE1_TEMPLATE = """
Analyze the student activity data and complete the following tasks:

1. Identify the student's learning style (visual, auditory, or kinesthetic).
2. Provide a 2–3 sentence explanation for your conclusion using evidence from the activity patterns.
3. Recommend two personalized content formats that match this learning style.
4. Suggest one potential risk of misclassification.

Student Activity:
{student_activity}

You MUST output your response strictly following the JSON schema below:

{format_instructions}
""".strip()


class LearningStyleService:
    def __init__(self, groq_api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.parser = PydanticOutputParser(pydantic_object=LearningStyleEvaluation)
        self.prompt = PromptTemplate(
            template=STAGE1_TEMPLATE,
            input_variables=["student_activity"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()
            },
        )
        self.llm = ChatGroq(
            api_key=groq_api_key,
            temperature=0.1,
            model=model,
        )
        self.chain = self.prompt | self.llm | self.parser

    def evaluate(self, student_activity: StudentActivity) -> LearningStyleEvaluation:
        payload = {
            "student_activity": {
                "activity": student_activity.activity
            }
        }
        return self.chain.invoke(payload)