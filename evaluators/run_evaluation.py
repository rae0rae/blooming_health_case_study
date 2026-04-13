import asyncio
import json
from prompts.eval_prompts import (
    get_eval_prompt,
    get_flags_and_suggestions_prompt,
    get_summary_prompt,
    TASK_COMPLETION_PROMPT,
    EMPATHY_PROMPT,
    CONCISENESS_PROMPT,
    NATURALNESS_PROMPT,
    SAFETY_PROMPT,
    CLARITY_PROMPT
)
from api.models.responses import (
    JudgeOutput,
    GradingStructure,
    EvaluationResponse,
    BatchEvaluationResponse
)

async def call_llm(system_prompt, model, client):
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": "Okay, understood. I will do my best to complete the task."}
        ]
    )
    return response.choices[0].message.content

async def run_evaluation(request, model, client) -> EvaluationResponse:
    dimensions = await get_dimensions(request, model, client)
    flags, suggestions = await get_flags_and_suggestions(dimensions, request, model, client)
    overall_score = calculate_overall_score(dimensions)
    return EvaluationResponse(
        overall_score=overall_score,
        dimensions=dimensions,
        flags=flags,
        suggestions=suggestions,
    )

async def run_batch_evaluation(request, model, client) -> BatchEvaluationResponse:
    results = await asyncio.gather(*[run_evaluation(req, model, client) for req in request.batch_request])
    scores = [r.overall_score for r in results]
    all_suggestions = [s for r in results for s in r.suggestions]
    flags = list(set(f for r in results for f in r.flags))
    summary = await get_summary(all_suggestions, model, client)
    return BatchEvaluationResponse(
        results=list(results),
        total = len(results),
        average_score=round(sum(scores)/len(scores), 1),
        success_rate=round(sum(1 for s in scores if s>=8)/ len(scores), 1),
        flags=flags,
        suggestions_summary=summary
    )

async def get_summary(suggestions, model, client) -> str:
    prompt = get_summary_prompt(suggestions)
    results = await call_llm(prompt, model, client)
    return results

def calculate_overall_score(dimensions: JudgeOutput) -> float:
    scores = [
        dimensions.task_completion.score,
        dimensions.empathy.score,
        dimensions.conciseness.score,
        dimensions.naturalness.score,
        dimensions.safety.score,
        dimensions.clarity.score,
    ]
    return round(sum(scores)/len(scores), 1)

async def get_dimensions(request, model, client) -> JudgeOutput:
    SYSTEM_PROMPT = get_eval_prompt(request)
    results = await asyncio.gather(
        call_llm(SYSTEM_PROMPT+TASK_COMPLETION_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+EMPATHY_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+CONCISENESS_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+NATURALNESS_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+SAFETY_PROMPT, model, client),
        call_llm(SYSTEM_PROMPT+CLARITY_PROMPT, model, client),
    )
    try:
        return JudgeOutput(
            task_completion=GradingStructure.model_validate(json.loads(results[0])),
            empathy=GradingStructure.model_validate(json.loads(results[1])),
            conciseness=GradingStructure.model_validate(json.loads(results[2])),
            naturalness=GradingStructure.model_validate(json.loads(results[3])),
            safety=GradingStructure.model_validate(json.loads(results[4])),
            clarity=GradingStructure.model_validate(json.loads(results[5])),
        )
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")

async def get_flags_and_suggestions(dimensions, request, model, client):
    flags_and_suggestions_prompt = get_flags_and_suggestions_prompt(request, dimensions)
    results = await call_llm(flags_and_suggestions_prompt, model, client)
    try:
        results = json.loads(results)
        flags = results.get("flags", [])
        suggestions = results.get("suggestions", [])
        return flags, suggestions
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM returned invalid JSON: {e}")