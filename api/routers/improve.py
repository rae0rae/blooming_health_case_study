from fastapi import APIRouter, Request
from api.models.requests import ImproveRequest
from api.models.responses import ImproveResponse
from evaluators.run_improve import run_improve
from core.constants import MODEL, client

router = APIRouter()

@router.post("/api/improve", response_model=ImproveResponse)
async def get_improvement(request: ImproveRequest):
    response = await run_improve(request, MODEL, client)
    return response