import pdfplumber


def extract_text_from_pdf(file_path: str) -> str:
    """Extract plain text from a PDF file, page by page."""
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
    return text.strip()


def chunk_text(text: str, chunk_size: int = 1000) -> list[str]:
    """Split text into ~chunk_size-character chunks, breaking on paragraph
    boundaries so a chunk never cuts a paragraph in half. Notes with several
    topics/sections end up as several chunks, which is what lets question
    generation spread across the whole document instead of just the start."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if current and len(current) + len(para) + 2 > chunk_size:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        chunks.append(current.strip())
    return chunks
