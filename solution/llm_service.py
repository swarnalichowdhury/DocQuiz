import os
import json
from pathlib import Path
from groq import Groq
from dotenv import load_dotenv

# Search for .env in project root or current dir
env_path = Path(__file__).resolve().parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)
else:
    load_dotenv()

SAMPLE_QUESTIONS = [
    {
        "question": "What is the primary purpose of the `__init__` method in a Python class?",
        "options": {
            "A": "To destroy an object when it is no longer needed",
            "B": "To act as a constructor that initializes object attributes",
            "C": "To inherit methods from a parent class",
            "D": "To declare class variables that are shared across all instances",
        },
        "correct_answer": "B",
        "explanation": "__init__ is a special constructor method that runs automatically when creating a new object to set up initial attribute values.",
        "difficulty": "easy",
        "topic": "The __init__ Method",
    },
    {
        "question": "In Python, what does the 'self' parameter in an instance method represent?",
        "options": {
            "A": "A reference to the current instance of the class",
            "B": "A global variable accessible by all classes",
            "C": "A reference to the parent superclass",
            "D": "The Python interpreter itself",
        },
        "correct_answer": "A",
        "explanation": "'self' refers to the specific instance of the object being created or manipulated.",
        "difficulty": "easy",
        "topic": "The __init__ Method",
    },
    {
        "question": "How do you define a class `Puppy` that inherits from a class `Dog` in Python?",
        "options": {
            "A": "class Puppy extends Dog:",
            "B": "class Puppy implements Dog:",
            "C": "class Puppy(Dog):",
            "D": "class Puppy inherits Dog:",
        },
        "correct_answer": "C",
        "explanation": "Python uses parentheses syntax `class Child(Parent):` to specify inheritance.",
        "difficulty": "medium",
        "topic": "Inheritance",
    },
    {
        "question": "What is the difference between a class variable and an instance variable in Python?",
        "options": {
            "A": "Class variables are private; instance variables are public",
            "B": "Class variables are shared across all instances; instance variables are unique to each object",
            "C": "Class variables are created with 'self.'; instance variables are defined directly in the class body",
            "D": "Class variables can only store numbers; instance variables store strings",
        },
        "correct_answer": "B",
        "explanation": "Class variables are defined in the class body and shared by all instances, while instance variables are bound to individual objects via self.",
        "difficulty": "medium",
        "topic": "Class Variables vs Instance Variables",
    },
    {
        "question": "How does Python signal that an attribute is intended for internal use only (encapsulation)?",
        "options": {
            "A": "Using the 'private' keyword before the variable declaration",
            "B": "By enclosing the attribute name in curly braces",
            "C": "By prefixing the variable name with a leading underscore (e.g., _balance)",
            "D": "By declaring it inside a static block",
        },
        "correct_answer": "C",
        "explanation": "By convention in Python, a single leading underscore (like `_balance`) indicates that an attribute is intended for internal use only.",
        "difficulty": "hard",
        "topic": "Encapsulation",
    },
    {
        "question": "Which concept allows `Dog.speak()` and `Cat.speak()` to be called interchangeably without knowing the exact class beforehand?",
        "options": {
            "A": "Polymorphism",
            "B": "Encapsulation",
            "C": "Data abstraction",
            "D": "Multiple inheritance",
        },
        "correct_answer": "A",
        "explanation": "Polymorphism allows different classes to implement methods with the same name, and the appropriate method executes based on the object's class.",
        "difficulty": "hard",
        "topic": "Polymorphism",
    },
    {
        "question": "What is the relationship modeled when `Puppy` inherits from `Dog`?",
        "options": {
            "A": "'has-a' relationship",
            "B": "'is-a' relationship",
            "C": "'uses-a' relationship",
            "D": "'part-of' relationship",
        },
        "correct_answer": "B",
        "explanation": "Inheritance models an 'is-a' relationship: a Puppy is a Dog.",
        "difficulty": "medium",
        "topic": "Inheritance",
    },
]


def get_client() -> Groq | None:
    # Always reload .env so edits take effect immediately without server restart
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key.strip() in ("", "your_key_here", "your_actual_key"):
        return None
    return Groq(api_key=api_key.strip())


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


def _get_best_model(client: Groq) -> str:
    """Find the best available model from the account's active models."""
    try:
        available = {m.id for m in client.models.list().data}
        preferred = [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "qwen/qwen3.8-27b",
        ]
        for model in preferred:
            if model in available:
                return model
        for m_id in available:
            if "whisper" not in m_id and "guard" not in m_id:
                return m_id
    except Exception:
        pass
    return "openai/gpt-oss-120b"


def generate_questions(chunks: list[str], num_questions: int = 5) -> list[dict]:
    """Generate multiple-choice questions covering all topics in the notes via Groq."""
    client = get_client()
    if client is None:
        raise ValueError(
            "GROQ_API_KEY is not set in .env! To generate custom quiz questions for ANY PDF, "
            "please add your free Groq API key to the .env file. (Get one free at https://console.groq.com)"
        )

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
    model_name = _get_best_model(client)
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return data["questions"]

