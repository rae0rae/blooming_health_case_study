# Hello!

Thank you for reading my case study! In this study we will be creating simple evaluations using LLM-as-judge for evaluations. The evaluation types are listed below, as well as steps, and a section on design/trade-offs.

## **Evaluation Types**

Below are the different types of evaluations that this code is capable of achieving and what their input should look like.

### *Single Evaluations*
This code works as a simple way to test LLM responses using an LLM-as-judge structure. Each inputted query will be graded on task completion, empathy, conciseness, naturalness, safety and clarity. The inputted query must be structured as follows:
```json 
{
  "context": {
    "conversation_history": [
      {
        "role": "user",
        "content": "what time is it"
      },
      {
        "role": "assistant",
        "content": "summertime"
      }
    ],
    "current_directive": "the assistant should give the user the time",
    "user_input": "what time is it"
  },
  "response": "summertime",
  "metadata": {
    "agent_id": "01",
    "prompt_version": "v0",
    "model": "llama4"
  }
}
```

### *Batch Evaluations*

Batch evaluation basically calls a list of single evaluations and provides a summary of all of the improvements that can be made at the end.
```json 
{
  "batch_request": [
    {
      "context": {
        "conversation_history": [
          {
            "role": "string",
            "content": "string"
          }
        ],
        "current_directive": "string",
        "user_input": "string"
      },
      "response": "string",
      "metadata": {
        "agent_id": "string",
        "prompt_version": "string",
        "model": "string"
      }
    },
    {
      "context": {
        "conversation_history": [
          {
            "role": "string",
            "content": "string"
          }
        ],
        "current_directive": "string",
        "user_input": "string"
      },
      "response": "string",
      "metadata": {
        "agent_id": "string",
        "prompt_version": "string",
        "model": "string"
      }
    }
  ]
}
```

### *Comparisons*

Comparison takes in a single directive and user input, and compares the responses of two prompts or models.
```json
{
  "context": {
    "conversation_history": [
      {
        "role": "string",
        "content": "string"
      }
    ],
    "current_directive": "string",
    "user_input": "string"
  },
  "response_a": "string",
  "response_b": "string",
  "a_metadata": {
    "agent_id": "string",
    "prompt_version": "string",
    "model": "string"
  },
  "b_metadata": {
    "agent_id": "string",
    "prompt_version": "string",
    "model": "string"
  }
}
```

### *Improvement Suggestions*

Takes in an existing response and provides an improved response and recommendations on how to improve the response. It also provides an improved score.
```json
{
  "context": {
    "conversation_history": [
      {
        "role": "string",
        "content": "string"
      }
    ],
    "current_directive": "string",
    "user_input": "string"
  },
  "response": "string",
  "metadata": {
    "agent_id": "string",
    "prompt_version": "string",
    "model": "string"
  },
  "existing_score": 0
}
```


## **Steps for Running Code**

### *1. Clone the repo*

Run:
```bash
git clone https://github.com/rae0rae/blooming_health_case_study.git
```
### *2. Copy .env.example and add your own Open AI key to the new .env file*

Run:
```bash
cp .env.example .env
```
And edit the new .env file. The .env file currently is OPENAI_API_KEY = "YOUR-API-KEY-HERE", replace YOUR-API-KEY-HERE with your personal key.

### *3. Install dependencies*
This code was built on top of the uvicorn ASGI so it works best with it! However if that is not installed, you can still make it work with pip.

```bash
uv sync #(preferred)
```

 OR 

```bash
pip install -r requirements.txt
```

### *4. Run the server*
```bash
uv run uvicorn main:app --reload
```

OR (if using pip)

```bash
uvicorn main:app --reload
```

### *5. Open http://127.0.0.1:8000/docs to test all endpoints!*

## **Design and Trade-offs**

### Endpoints

Endpoints and routers are held in the api folder. Pydantic data modeling classes are in the models folder, with the api routers being held in the routers folder (creative names, i know.)

First I built the api endpoints and routers, separating each evaluator into its own router. This was specifically to match the case study rubric but also was the most organized approach and led to an easy, organized build for the rest of the system. This also gave me a good place to start with class declarations and pydantic as well.
Once the endpoints and data structures were settled, I needed to build the actual evaluation agent.

### LLM Evaluators and prompts

Prompts are all held in the prompts folder with separate prompts for each evaluator.

Each evaluator has its own base prompt that took in each request's data so that it had context within the prompt, allowing the LLM to make a more informed decision. I decided to separate each dimension prompt for higher accuracy and lower probability of the outputted JSON being invalid/hallucinated. Each dimension is scored concurrently using asyncio.gather to reduce latency. Since there are 6 calls being made at once, I also added return_exceptions=True, in case 
When calling the actual LLM for the dimensions, the prompt being passed in was both the evaluator's base prompt, and the individual dimensions prompt. The base prompt is a very short prompt that gives context to the LLM, including the appropriate output structure, where the dimension-specific prompt gives specific instructions for the domain being evaluated. Token usage was kept in mind when composing the prompts, especially the base prompt.

Flags and suggestions are its own separate prompt so that the judge can use the previously calculated dimensions as context for its output.

For batch evaluation, flags and suggestions_summary is also done at the end so that it has the complete context. Flags in batch_evaluation takes all of the outputted lists and creates a set to avoid duplicates, but in production this would be better to have an actual filter or another LLM consolidating the list. No matter what, performing this step at the end of the rest of the evaluation would still be the best choice in my opinion.

The prompts themselves contain a chain-of-thought reasoning structure, which increases reliability and accuracies in its output. With more time and evaluation, I would also add few shot examples to the prompt for better results, especially for outputs that are not reliable.

### What I would improve with more time

If I had more time, I would make is to look more closely at LLM outputs and create more data validation error checks for the LLM responses. I would do so especially with the dimensions call, where 6 llm calls are made at once, and if one fails they all do. It is best practice to always keep track of any data validation errors and have a plan b such as retrying x amount of times, moving on to the next evaluation, or exiting with an error that specifies where the system broke.

Another thing I would do is spend more time improving the prompts and testing for edge cases. I also would have liked to have had the evaluators, batch evaluation especially, output into a dataframe so that we could examine the results in a more organized way and see where improvements could be made. I would also set up batch evaluations for compare and improve and try to simplify/consolidate the code and prompts a bit more to be less repetitive.
