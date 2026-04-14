import asyncio
import json
from api.models.responses import ImproveResponse
from evaluators.run_evaluation import call_llm, run_evaluation
from prompts.improve_prompts import get_improve_prompt


async def run_improve(request, model, client) -> ImproveResponse:
    original_score = request.existing_score if request.existing_score else await calculate_old_score(request, model, client)
    improved_response, changes_made = await get_improve_and_changes_made(request, model, client)
    new_score = await calculate_new_score(request, model, client, improved_response)
    return ImproveResponse(
        original_score=original_score,
        improved_response=improved_response,
        improved_score=new_score,
        changes_made=changes_made
    )
async def get_improve_and_changes_made(request, model, client) -> tuple[str, list[str]]:
    prompt = get_improve_prompt(request)
    response = await call_llm(prompt, model, client)
    try:
        response = json.loads(response)
        improved_response = response.get("improved_response", "")
        changes_made = response.get("changes_made", [])
        return improved_response, changes_made
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")


async def calculate_old_score(request, model, client) -> float:
    old_eval = await run_evaluation(request, model, client)
    return old_eval.overall_score

async def calculate_new_score(request, model, client, new_response) -> float:
    modified_request = request.model_copy(update={"response": new_response})
    new_eval = await run_evaluation(modified_request, model, client)
    return new_eval.overall_score


