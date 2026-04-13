from pydantic import BaseModel, Field
from typing import Literal, Optional

class GradingStructure(BaseModel):
    score: float = Field(ge=0.0,le=10.0)
    reasoning: str

class JudgeOutput(BaseModel):
    task_completion: GradingStructure
    empathy: GradingStructure
    conciseness: GradingStructure
    naturalness: GradingStructure
    safety: GradingStructure
    clarity: GradingStructure

class EvaluationResponse(BaseModel):
    overall_score: float = Field(ge=0.0, le=10.0)
    dimensions: JudgeOutput #fill later
    flags: list[str] = Field(default_factory=list)
    suggestions: list[str] = Field(default_factory=list)

class ImproveResponse(BaseModel):
    original_score: float = Field(ge=0.0,le=10.0)
    improved_response: str
    improved_score: float = Field(ge=0.0, le=10.0)
    changes_made: list[str]

class CompareReasoning(BaseModel):
    winner: Literal["a", "b", "tie"]
    reasoning: str

class CompareJudgeOutput(BaseModel):
    task_completion: CompareReasoning
    empathy: CompareReasoning
    conciseness: CompareReasoning
    naturalness: CompareReasoning
    safety: CompareReasoning
    clarity: CompareReasoning

class CompareResponse(BaseModel):
    winner: Literal["a", "b", "tie"]
    comparison: CompareJudgeOutput
    recommendation: str

class BatchEvaluationResponse(BaseModel):
    results: list[EvaluationResponse]
    total: int
    average_score: float = Field(ge=0.0, le=10.0)
    success_rate: float = Field(ge=0.0, le=1.0)
    flags: list[str] = Field(default_factory=list)
    suggestions_summary: Optional[str] = None