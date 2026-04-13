from fastapi import APIRouter, Request
from api.models.requests import EvaluationRequest, BatchEvaluationRequest
from api.models.responses import EvaluationResponse, BatchEvaluationResponse
from evaluators.run_evaluation import run_evaluation, run_batch_evaluation
from core.constants import MODEL, client

router = APIRouter()

@router.post("/api/evaluate", response_model=EvaluationResponse) #validate output
async def evaluate_responses(request: EvaluationRequest):
    response = await run_evaluation(request, MODEL, client)
    return response

@router.post("/api/evaluate/batch", response_model=BatchEvaluationResponse)
async def batch_evaluate(request: BatchEvaluationRequest):
    response = await run_batch_evaluation(request, MODEL, client)
    return response