import asyncio
import json
from api.models.responses import CompareResponse, CompareReasoning, CompareJudgeOutput
from evaluators.run_evaluation import call_llm
from prompts.compare_prompts import (
    get_compare_prompt,
    get_recommendations_prompt,
    TASK_COMPLETION_COMPARE_PROMPT,
    EMPATHY_COMPARE_PROMPT,
    CONCISENESS_COMPARE_PROMPT,
    NATURALNESS_COMPARE_PROMPT,
    SAFETY_COMPARE_PROMPT,
    CLARITY_COMPARE_PROMPT
)

async def run_comparison(request, model, client) -> CompareResponse:
    dimensions = await get_compare_dimensions(request, model, client)
    winner = calculate_winner(dimensions)
    recommendation = await get_recommendation(dimensions, winner, model, client)
    return CompareResponse(
        winner=winner,
        comparison=dimensions,
        recommendation=recommendation,
    )

def calculate_winner(dimensions) -> str:
    votes = [
        dimensions.task_completion.winner,
        dimensions.empathy.winner,
        dimensions.conciseness.winner,
        dimensions.naturalness.winner,
        dimensions.safety.winner,
        dimensions.clarity.winner,
    ]
    a_count = votes.count("a")
    b_count = votes.count("b")
    if a_count > b_count:
        return "a"
    elif b_count > a_count:
        return "b"
    else:
        return "tie"

async def get_recommendation(dimensions, winner, model, client) -> str:
    prompt = get_recommendations_prompt(dimensions, winner)
    response = await call_llm(prompt, model, client)
    return response

async def get_compare_dimensions(request, model, client) -> CompareJudgeOutput:
    SYSTEM_PROMPT = get_compare_prompt(request)
    results = await asyncio.gather(
        call_llm(SYSTEM_PROMPT+TASK_COMPLETION_COMPARE_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+EMPATHY_COMPARE_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+CONCISENESS_COMPARE_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+NATURALNESS_COMPARE_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+SAFETY_COMPARE_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+CLARITY_COMPARE_PROMPT, model, client),
    )
    try:
        return CompareJudgeOutput(
            task_completion=CompareReasoning.model_validate(json.loads(results[0])),
            empathy=CompareReasoning.model_validate(json.loads(results[1])),
            conciseness=CompareReasoning.model_validate(json.loads(results[2])),
            naturalness=CompareReasoning.model_validate(json.loads(results[3])),
            safety=CompareReasoning.model_validate(json.loads(results[4])),
            clarity=CompareReasoning.model_validate(json.loads(results[5])),
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")