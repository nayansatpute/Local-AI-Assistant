from pydantic import BaseModel, Field
from typing import Optional

class AIResponse(BaseModel):
    """
    This is our contract with the AI.
    Every response MUST have these exact fields.
    Pydantic will reject anything that doesn't match.
    """
    answer: str = Field(
        ...,
        description="Main answer to the question"
    )
    confidence: str = Field(
        ...,
        description="Must be: high / medium / low"
    )
    key_points: list[str] = Field(
        ...,
        description="Exactly 3 bullet points"
    )
    word_count: Optional[int] = Field(
        None,
        description="Word count of the answer"
    )