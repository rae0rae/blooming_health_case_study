import os
from dotenv import load_dotenv
load_dotenv()

from openai import AsyncOpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

MODEL = "gpt-4o-mini"
client = AsyncOpenAI()