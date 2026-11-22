
from io import BytesIO
import re

from pypdf import PdfReader


def extract_pdf(pdf_bytes: bytes) -> dict:
    """Extract selectable text page-by-page and retain page numbers."""
    reader = PdfReader(BytesIO(pdf_bytes))
    pages = []
    all_text = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        # Replace three or more consecutive newlines with two.
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        if text:
            pages.append({
                "page": page_number,
                "text": text
            })
            all_text.append(f"[Page {page_number}]\n{text}")

    return {
        "pages": pages,
        "text": "\n\n".join(all_text)
    }


def split_into_chunks(
    pages: list,
    max_chars: int = 11000,
    overlap: int = 500
) -> list:
    """Split extracted page text into manageable overlapping chunks."""
    chunks = []
    current_text = ""
    current_pages = []

    for page in pages:
        page_text = f"[Page {page['page']}]\n{page['text']}"

        if current_text and len(current_text) + len(page_text) > max_chars:
            chunks.append({
                "text": current_text,
                "pages": sorted(set(current_pages))
            })

            current_text = current_text[-overlap:] + "\n\n" + page_text
            current_pages = current_pages[-1:] + [page["page"]]

        else:
            current_text = (
                current_text + "\n\n" + page_text
            ).strip()

            current_pages.append(page["page"])

    if current_text.strip():
        chunks.append({
            "text": current_text,
            "pages": sorted(set(current_pages))
        })

    return chunks


def rank_chunks(
    chunks: list,
    question: str,
    limit: int = 4
) -> list:
    """Simple keyword-overlap retrieval."""

    stop_words = {
        "what", "when", "where", "which", "who", "why", "how",
        "does", "did", "the", "and", "for", "with", "from",
        "this", "that", "are", "was", "were", "can", "could",
        "would", "should", "about", "paper", "research",
        "explain", "tell", "please", "into", "their", "they",
        "them", "have", "has", "had", "its", "our", "your", "you"
    }

    terms = {
        token.lower()
        for token in re.findall(r"[A-Za-z0-9]{3,}", question)
        if token.lower() not in stop_words
    }

    scored = []

    for index, chunk in enumerate(chunks):
        words = set(
            re.findall(r"[A-Za-z0-9]{3,}", chunk["text"].lower())
        )

        score = len(terms.intersection(words))
        scored.append((score, index, chunk))

    scored.sort(
        key=lambda item: (item[0], -item[1]),
        reverse=True
    )

    selected = [
        item[2]
        for item in scored[:limit]
        if item[0] > 0
    ]

    if not selected:
        selected = chunks[:min(limit, len(chunks))]

    return selected
