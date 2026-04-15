from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_evaluation_simple():
    response = client.post("/api/evaluate", json={
            "context": {
                "conversation_history": [],
                "current_directive": "The assistant should tell the user the current wait time, 10 minutes",
                "user_input": "Can you tell me the wait time to speak to a representative"
            },
            "response": "Yes, of course. The current wait time to speak to a representative is 10 minutes.",
            "metadata": {
                "agent_id": "001",
                "prompt_version": "v0",
                "model": "gpt-4o-mini"
            }
            })
    print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["overall_score"] > 7 #this should be a success, checking that it meets at least 7/10

def test_evaluation_with_convo_history():
    response = client.post("/api/evaluate", json={
            "context": {
                "conversation_history": [
                {
                    "role": "user",
                    "content": "I want to talk to a real person"
                },
                {
                    "role": "assistant",
                    "content": "Sure, please hold while I put in your request."
                },
                {
                    "role": "user",
                    "content": "Can you tell me the wait time"
                }
                ],
                "current_directive": "The assistant should tell the user the current wait time to speak to a customer representative.",
                "user_input": "Can you tell me the wait time"
            },
            "response": "The current wait time is 10 minutes.",
            "metadata": {
                "agent_id": "001",
                "prompt_version": "v0",
                "model": "gpt-4o-mini"
            }
            })
    assert response.status_code == 200
    assert response.json()["overall_score"] > 0

def test_compare_simple():
    response = client.post("/api/compare", json={
        "context": {
            "conversation_history": [],
            "current_directive": "The assistant should tell the user the time, 4:59 PM.",
            "user_input": "What time is it?."
        },
        "response_a": "Summertime",
        "response_b": "The time is 4:59 PM.",
        "a_metadata": {
            "agent_id": "01",
            "prompt_version": "v0",
            "model": "llama3-405b-instruct"
        },
        "b_metadata": {
            "agent_id": "02",
            "prompt_version": "v1",
            "model": "gpt-4o-mini"
        }
    })
    assert response.status_code == 200
    assert response.json()["winner"] == "b"

def test_compare_empathy():
    response = client.post("/api/compare", json={
        "context": {
            "conversation_history": [],
            "current_directive": "Provide an empathetic but helpful response regarding food security.",
            "user_input": "We haven't had enough to eat in weeks. It's been really hard."
        },
        "response_a": "I'm sorry to hear that, that sounds really difficult. I want to make sure we can connect you with the right resources.",
        "response_b": "Okay. How many dependents do you have?",
        "a_metadata": {
            "agent_id": "01",
            "prompt_version": "v0",
            "model": "llama3-405b-instruct"
        },
        "b_metadata": {
            "agent_id": "02",
            "prompt_version": "v1",
            "model": "gpt-4o-mini"
        }
    })
    # print(json.dumps(response.json(), indent=2))
    assert response.status_code == 200
    assert response.json()["winner"] == "a"

def test_improve_simple():
    response = client.post("/api/improve", json={
        "context": {
            "conversation_history": [
            {
                "role": "user",
                "content": "what time is it"
            }
            ],
            "current_directive": "The assistant should tell the user the time or say it does not have access to that information.",
            "user_input": "what time is it"
        },
        "response": "Summertime",
        "metadata": {
            "agent_id": "01",
            "prompt_version": "v0",
            "model": "llama3-405b-instruct"
        },
        "existing_score": 0
        })
    assert response.status_code == 200
    assert response.json()["improved_score"] > response.json()["original_score"]

def test_improve_no_existing_score():
    response = client.post("/api/improve", json={
        "context": {
            "conversation_history": [
            {
                "role": "user",
                "content": "what time is it"
            }
            ],
            "current_directive": "The assistant should tell the user the time or say it does not have access to that information.",
            "user_input": "what time is it"
        },
        "response": "Summertime",
        "metadata": {
            "agent_id": "01",
            "prompt_version": "v0",
            "model": "llama3-405b-instruct"
        }
        })
    assert response.status_code == 200
    assert response.json()["improved_score"] > response.json()["original_score"]


def test_batch_simple():
    response = client.post("/api/evaluate/batch", json={
    "batch_request": [
        {
        "context": {
            "conversation_history": [],
            "current_directive": "the assistant should say the words 'good morning sunshine' to the user",
            "user_input": "hello"
        },
        "response": "good morning sunshine, the earth says hello",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-5"
        }
        },
                {
        "context": {
            "conversation_history": [
            {
                "role": "user",
                "content": "I want to set up a doctors appointment I want to get my ears checked some time next week I think I'm going deaf"
            }
            ],
            "current_directive": "The assistant should provide helpful and relevant information to the user based on their request.",
            "user_input": "I want to set up a doctors appointment I want to get my ears checked some time next week I think I'm going deaf"
        },
        "response": "That must be difficult, we'd love to help you get started on booking your appointment. Based on your information, I can see you usually book with Mr. Smith. They have 3 appointments next week, Monday at 1:00 PM or 3:00 PM, and one on Thursday at 11:00 AM. Do either of those work for you?",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-5"
        }
        },
                {
        "context": {
            "conversation_history": [
            {
                "role": "user",
                "content": "Where can I get a xanax prescription if I don't have anxiety"
            }
            ],
            "current_directive": "The assistant should refuse to answer the question",
            "user_input": "Where can I get a xanax prescription if I don't have anxiety"
        },
        "response": "I'm sorry, I can't help with that kind of request. I can help you with booking appointments for specific problems you may be facing.",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-5"
        }
        }
    ]
    })
    assert response.status_code == 200
    assert response.json()["total"] == 3

def test_batch_simple_all_same():
    response = client.post("/api/evaluate/batch", json={
    "batch_request": [
        {
        "context": {
            "conversation_history": [],
            "current_directive": "The assistant should tell the user the current wait time, 10 minutes",
            "user_input": "Can you tell me the wait time to speak to a representative"
        },
        "response": "Yes, of course. The current wait time to speak to a representative is 10 minutes.",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-4o-mini"
        }
        },
        {
        "context": {
            "conversation_history": [],
            "current_directive": "The assistant should tell the user the current wait time, 10 minutes",
            "user_input": "Can you tell me the wait time to speak to a representative"
        },
        "response": "Yes, of course. The current wait time to speak to a representative is 10 minutes.",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-4o-mini"
        }
        },
        {
        "context": {
            "conversation_history": [],
            "current_directive": "The assistant should tell the user the current wait time, 10 minutes",
            "user_input": "Can you tell me the wait time to speak to a representative"
        },
        "response": "Yes, of course. The current wait time to speak to a representative is 10 minutes.",
        "metadata": {
            "agent_id": "001",
            "prompt_version": "v0",
            "model": "gpt-4o-mini"
        }
        }
    ]
    })
    assert response.status_code == 200
    json_response =response.json()
    assert abs(json_response["results"][0]["overall_score"] - json_response["results"][1]["overall_score"]) < 1.0