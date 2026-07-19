import sys
from pathlib import Path
from pdf_service import extract_text_from_pdf, chunk_text
from llm_service import generate_questions

DEFAULT_PDF = Path(__file__).parent.parent / "sample_notes" / "python_oop_basics.pdf"

if __name__ == "__main__":
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_PDF)
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text)
    questions = generate_questions(chunks)
    for q in questions:
        print(q)
