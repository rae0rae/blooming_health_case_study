from pydantic import BaseModel, Field
from typing import Optional

class ConvoStructure(BaseModel):
    role: str
    content: str
    
class Context(BaseModel):
    conversation_history: list[ConvoStructure] = Field(default_factory=list)
    current_directive: str
    user_input: str

class Metadata(BaseModel):
    agent_id:str
    prompt_version:str
    model:str

class EvaluationRequest(BaseModel):
    context: Context
    response: str
    metadata: Metadata

class BatchEvaluationRequest(BaseModel):
    batch_request: list[EvaluationRequest]

class CompareRequest(BaseModel):
    context: Context
    response_a: str
    response_b: str
    a_metadata: Metadata
    b_metadata: Metadata

class ImproveRequest(BaseModel):
    context: Context
    response: str
    metadata: Metadata
    existing_score: Optional[float] = None