"""
LLM client – Hugging Face Chat Completion API
"""

from __future__ import annotations

from typing import List, Tuple, Dict
from huggingface_hub import InferenceClient
from utils.pdf_processor import find_relevant_chunks

# ------------------------------------------------------------------
# Chat-compatible models
# ------------------------------------------------------------------

HF_MODELS = {
    "Qwen 2.5 7B (Recommended)": "Qwen/Qwen2.5-7B-Instruct",
    "Qwen 2.5 72B": "Qwen/Qwen2.5-72B-Instruct",
    "Llama 3.1 8B": "meta-llama/Llama-3.1-8B-Instruct",
}

NOT_FOUND_PHRASES = (
    "not available in the provided document",
    "not mentioned in the document",
    "cannot find",
    "not discussed",
    "not found in the document",
)

SYSTEM_PROMPT = """
You are DocMind AI.

Rules:

1. ONLY answer using the document context.
2. Never make up facts.
3. If the answer isn't present, reply:
   "This information is not available in the provided document."
4. Explain clearly using headings and bullet points.
5. Keep answers concise but complete.
"""

DEFAULT_MODEL = "Qwen/Qwen2.5-7B-Instruct"


def get_answer(
    question: str,
    doc_chunks: List[str],
    chat_history: List[Dict],
    api_key: str,
    model: str = DEFAULT_MODEL,
) -> Tuple[str, str]:

    try:

        client = InferenceClient(api_key=api_key)

        relevant = find_relevant_chunks(
            question,
            doc_chunks,
            top_k=5,
        )

        context = "\n\n".join(relevant)

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            }
        ]

        for msg in chat_history[-8:]:
            messages.append(
                {
                    "role": msg["role"],
                    "content": msg["content"],
                }
            )

        messages.append(
            {
                "role": "user",
                "content": f"""
Document Context:

{context}

Question:

{question}
""",
            }
        )

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=1200,
            temperature=0.2,
        )

        answer = response.choices[0].message.content.strip()

        source = "document"

        if any(x in answer.lower() for x in NOT_FOUND_PHRASES):
            source = "not found"

        return answer, source

    except Exception as e:

        error = str(e)

        if "401" in error:
            return (
                "❌ Invalid Hugging Face API Token.",
                "error",
            )

        if "429" in error:
            return (
                "❌ Rate limit exceeded. Please wait a minute.",
                "error",
            )

        if "503" in error:
            return (
                "❌ Model is loading. Please try again in 30 seconds.",
                "error",
            )

        return (
            f"❌ {error}",
            "error",
        )