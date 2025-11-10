# translator/openai_model.py
from __future__ import annotations
import os
from openai import OpenAI

_client = None

def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    return _client

def translate_with_openai(prompt: str) -> str:
    """
    Uses Responses API (recommended). Returns plain text.
    """
    client = _get_client()
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    resp = client.responses.create(
        model=model,
        input=prompt,
        instructions="You are a strict code-to-code translator. Output only code.",
        temperature=0
    )
    # The SDK exposes a convenience to combine outputs:
    try:
        return resp.output_text
    except Exception:
        # Fallback: stitch text parts manually
        chunks = []
        for item in (resp.output or []):
            if hasattr(item, "content"):
                for c in item.content:
                    if c.type == "output_text":
                        chunks.append(c.text)
                    elif c.type == "input_text":
                        # ignore
                        pass
        return "".join(chunks).strip()
