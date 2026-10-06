import os, re, json
import fitz
from sentence_transformers import SentenceTransformer
import faiss

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
UPLOAD_DIR = os.path.join(BASE, "uploads")
VECTOR_DIR = os.path.join(BASE, "vectorstores")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)
_MODEL = None

def embedding_model():
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer(os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    return _MODEL

def extract_pdf(path):
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text("text").strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    doc.close()
    return pages

def clean(text):
    return re.sub(r"\s+", " ", text).strip()

def chunk_pages(pages, chunk_size=900, overlap=150):
    chunks = []
    for page in pages:
        text = clean(page["text"])
        start = 0
        while start < len(text):
            end = min(len(text), start + chunk_size)
            if text[start:end]:
                chunks.append({"text": text[start:end], "page": page["page"]})
            if end >= len(text):
                break
            start = end - overlap
    return chunks

def build_index(doc_id, chunks):
    texts = [c["text"] for c in chunks]
    vectors = embedding_model().encode(texts, normalize_embeddings=True, show_progress_bar=False)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors.astype("float32"))
    faiss.write_index(index, os.path.join(VECTOR_DIR, f"{doc_id}.faiss"))
    with open(os.path.join(VECTOR_DIR, f"{doc_id}.json"), "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    return len(chunks)

def retrieve(doc_id, query, k=5):
    index_path = os.path.join(VECTOR_DIR, f"{doc_id}.faiss")
    data_path = os.path.join(VECTOR_DIR, f"{doc_id}.json")
    if not os.path.exists(index_path) or not os.path.exists(data_path):
        return []
    index = faiss.read_index(index_path)
    with open(data_path, encoding="utf-8") as f:
        chunks = json.load(f)
    query_vector = embedding_model().encode([query], normalize_embeddings=True).astype("float32")
    scores, ids = index.search(query_vector, min(k, len(chunks)))
    return [{**chunks[idx], "score": float(score)} for score, idx in zip(scores[0], ids[0]) if idx >= 0]
