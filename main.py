import os
from dotenv import load_dotenv
from openai import OpenAI
import argparse

load_dotenv()
api_key = os.environ.get("OPENROUTER_API_KEY")

if api_key is None:
    raise RuntimeError("API key was not found")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
)

parser = argparse.ArgumentParser(description="Chatbot")
parser.add_argument("user_prompt", type=str, help="User prompt")
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
args = parser.parse_args()

messages = [
    {"role": "user", "content": args.user_prompt},
]

response = client.chat.completions.create(
    model="anthropic/claude-haiku-5.5",
    messages=messages,
)

if response.usage:
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens

        print(f"Prompt tokens: {prompt_tokens}")
        print(f"Response tokens: {completion_tokens}")

    print(response.choices[0].message.content)
else:
    raise RuntimeError("API request failed")
