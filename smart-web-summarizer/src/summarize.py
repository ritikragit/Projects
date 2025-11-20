
import os
from dotenv import load_dotenv
from openai import OpenAI
from .prompts import SYSTEM_PROMPT, USER_PROMPT_PREFIX

load_dotenv()
client = OpenAI()

def summarize_text(text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT_PREFIX + text}
    ]

    res = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=messages
    )
    return res.choices[0].message.content
