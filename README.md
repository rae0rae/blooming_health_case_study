#### Hello!

Thank you for reading my case study! In this study we will be creating simple evaluations using LLM-as-judge for evaluations. The evaluation types are listed below, as well as steps, and a section on design/trade-offs.

### **Evaluation Types**

Below are the different types of evaluations that this code is capable of achieving and what their input should look like.

## *Single Evaluations*
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

## *Batch Evaluations*

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

## *Comparisons*

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

## *Improvement Suggestions*

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


### **Steps for Running Code**

## *1. Clone the repo*

Run:
```bash
git clone https://github.com/rae0rae/blooming_health_case_study.git
```
## *2. Copy .env.example and add your own Open AI key to the new .env file*

Run:
```bash
cp .env.example .env
```
And edit the new .env file. The .env file currently is OPENAI_API_KEY = "YOUR-API-KEY-HERE", replace YOUR-API-KEY-HERE with your personal key.

## *3. Install dependencies*
This code was built on top of the uvicorn ASGI so it works best with it! However if that is not installed, you can still make it work with pip.

```bash
uv sync #(preferred)
```

 OR 

```bash
pip install -r requirements.txt
```

## *4. Run the server*
```bash
uv run uvicorn main:app --reload
```

OR (if using pip)

```bash
uvicorn main:app --reload
```

## *5. Open http://127.0.0.1:8000/docs to test all endpoints!*

### **Design and Trade-offs**

First I built the api posts and routers, separating each evaluator into its own router. This was specifically to match the case study rubric but also was the most organized approach and led to an easy, organized build for the rest of the system. This also gave me a good place to start with class declarations and pydantic.
Once the endpoints and data structures were settled, I needed to build the actual evaluation agent.

Each evaluator, evaluate, compare, and improve had their own base prompt that took in each request's data so that it had context and was able to make a more informed decision. For the dimensions themselves, I decided to create a prompt for each. When calling the actual LLM, the prompt being passed in was both this base prompt (called system prompt in the code, although the name is not exactly accurate), and the individual dimensions prompt. I separated each dimensions prompt for higher accuracy and lower probability of the outputted JSON being hallucinated. Each dimension prompted llm call is called with asyncio.gather to reduce latency.

Flags and suggestions are its own separate prompt so that the judge can use the previously calculated dimensions as context for its output.

For batch evaluation, flags and suggestions_summary is also done at the end so that it has the complete context. Flags in batch_evaluation just takes all of the outputted lists and creates a set to avoid duplicates, but in production this would be better to have an actual filter or another LLM consolidating the list.

If I had more time, I would spend more time improving the prompts and testing for edge cases. I would have liked to have had the evaluators, batch evaluation especially, output into a dataframe so that we could examine the results in a more organized way and see where improvements could be made. I would also set up batch evaluations for compare and improve. 

Another improvement I would make is to look more closely at LLM outputs and create more data validation error checks for the LLM responses. Since there are so many calls going on in one execution and their output is not always perfectly structured, it would be best practice to always keep track of these and have a plan b such as retrying or exiting with a specific error.
