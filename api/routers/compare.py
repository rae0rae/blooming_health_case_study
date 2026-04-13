from fastapi import APIRouter, Request
from api.models.requests import CompareRequest
from api.models.responses import CompareResponse
from evaluators.run_comparison import run_comparison
from core.constants import MODEL, client

router = APIRouter()

@router.post("/api/compare", response_model=CompareResponse)
async def compare_responses(request: CompareRequest):
    response = await run_comparison(request, MODEL, client)
    return response
