"""
LLM configuration for the LearNexo Content Engine.
Uses Groq (llama-3.3-70b-versatile) via langchain-groq.
"""

import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()


def get_llm(temperature: float = 0.2) -> ChatGroq:
    """
    Return a configured Groq LLM instance.

    Reads GROQ_API_KEY from environment (set in .env or system environment).
    Raises a clear error if the key is missing.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. "
            "Add it to your .env file or set it as an environment variable.\n"
            "Example: GROQ_API_KEY=gsk_..."
        )
    return ChatGroq(
        api_key=api_key,
        model="llama-3.3-70b-versatile",
        temperature=temperature,
    )


# Shared instances used across modules
# Lower temperature for structured JSON outputs (more deterministic)
llm_structured = get_llm(temperature=0.1)

# Slightly higher temperature for richer creative content
llm_creative = get_llm(temperature=0.3)
