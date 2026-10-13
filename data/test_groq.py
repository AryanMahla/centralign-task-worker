
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not key:
    raise SystemExit("GROQ_API_KEY is missing from .env")

client = Groq(api_key=key)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Say hello in one short sentence.",
            }
        ],
        max_tokens=100,
    )

    print("Model:", model)
    print("Finish reason:", response.choices[0].finish_reason)
    print("Message:", repr(response.choices[0].message.content))
    print("Reasoning:", repr(
        getattr(response.choices[0].message, "reasoning", None)
    ))
    print("Usage:", response.usage)

except Exception as exc:
    print(f"Request failed: {type(exc).__name__}: {exc}")
