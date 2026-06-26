from __future__ import annotations
import io, re
from typing import Tuple, List
import pypdf

def extract_text_from_pdf(uploaded_file) -> Tuple[str, int]:
    try:
        pdf_bytes = uploaded_file.read()
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        page_count = len(reader.pages)
        pages_text = [page.extract_text() or "" for page in reader.pages]
        full_text = "\n\n".join(pages_text)
        full_text = re.sub(r"\n{3,}", "\n\n", full_text)
        full_text = re.sub(r"[ \t]{2,}", " ", full_text)
        return full_text.strip(), page_count
    except Exception as exc:
        print(f"[pdf_processor] error: {exc}")
        return "", 0

def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> List[str]:
    if not text:
        return []
    paragraphs = re.split(r"\n{2,}", text)
    chunks, current_chunk = [], ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(para) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
            for i in range(0, len(para), chunk_size - overlap):
                sub = para[i : i + chunk_size]
                if sub.strip():
                    chunks.append(sub.strip())
            continue
        if len(current_chunk) + len(para) + 2 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = current_chunk[-overlap:] + "\n\n" + para if overlap else para
        else:
            current_chunk = (current_chunk + "\n\n" + para).strip() if current_chunk else para
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    return [c for c in chunks if c]

def find_relevant_chunks(question: str, chunks: List[str], top_k: int = 5) -> List[str]:
    if not chunks:
        return []
    stop_words = {
        "what","when","where","which","who","whom","whose","why","how",
        "does","did","was","were","are","have","has","had","will","would",
        "could","should","shall","may","might","must","can","the","this",
        "that","these","those","and","but","for","with","from","about",
        "into","through","during","before","after","please","tell","give",
        "list","explain","describe","show",
    }
    q_words = {
        w.lower() for w in re.findall(r"\b\w+\b", question)
        if len(w) > 3 and w.lower() not in stop_words
    }
    if not q_words:
        return chunks[:top_k]
    def score(chunk: str) -> int:
        cl = chunk.lower()
        return sum(1 for w in q_words if w in cl)
    return sorted(chunks, key=score, reverse=True)[:top_k]