import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _select_content(chunks: list[str], budget: int = 12000) -> str:
    """Pick content spread evenly across all chunks so multi-topic notes
    aren't reduced to just their opening section. Each chunk contributes up
    to an equal share of the total character budget."""
    if not chunks:
        return ""
    total_len = sum(len(c) for c in chunks)
    if total_len <= budget:
        return "\n\n".join(chunks)
    per_chunk_budget = budget // len(chunks)
    return "\n\n".join(c[:per_chunk_budget] for c in chunks)


def generate_questions(chunks: list[str], num_questions: int = 5) -> list[dict]:
    """Generate multiple-choice questions covering all topics in the notes via Groq."""
    num_questions = max(num_questions, len(chunks))
    notes = _select_content(chunks)
    prompt = f"""You are an expert teacher. The notes below may cover multiple topics
or sections. Generate {num_questions} multiple-choice questions that together cover
the different topics found in the notes — don't cluster all the questions around
only one section.

For each question return: question, options (A, B, C, D), correct_answer (letter),
explanation, difficulty (easy/medium/hard), topic.

Return ONLY a JSON object with a "questions" array.

Notes:
{notes}
"""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return data["questions"]
