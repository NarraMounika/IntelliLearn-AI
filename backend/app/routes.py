import os, uuid
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from .db import *
from .auth import require_auth, token_for
from .services.documents import UPLOAD_DIR, extract_pdf, chunk_pages, build_index, retrieve
from .services.ai import pdf_chat, study_material, generate
from .services.youtube import transcript, search

api = Blueprint("api", __name__)

def public_user(user):
    return {"id": user["id"], "name": user["name"], "email": user["email"], "role": user["role"]}

@api.post("/auth/register")
def register():
    data = request.get_json() or {}
    if any(not data.get(key) for key in ("name", "email", "password", "role")):
        return jsonify({"error":"name, email, password and role are required"}), 400
    if data["role"] not in ("student", "faculty"):
        return jsonify({"error":"Invalid role"}), 400
    if len(data["password"]) < 6:
        return jsonify({"error":"Password must be at least 6 characters"}), 400
    try:
        user = create_user(data["name"], data["email"], data["password"], data["role"])
    except Exception as exc:
        if "UNIQUE" in str(exc):
            return jsonify({"error":"Email already registered"}), 409
        raise
    return jsonify({"token": token_for(user), "user": public_user(user)})

@api.post("/auth/login")
def login():
    data = request.get_json() or {}
    user = authenticate(data.get("email", ""), data.get("password", ""))
    if not user:
        return jsonify({"error":"Invalid email or password"}), 401
    return jsonify({"token": token_for(user), "user": public_user(user)})

@api.get("/auth/me")
@require_auth()
def me():
    return jsonify({"user": get_user(request.user["sub"])})

@api.get("/documents")
@require_auth()
def documents():
    return jsonify({"documents": list_documents()})

@api.post("/documents/upload")
@require_auth("faculty")
def upload_document():
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"error":"PDF file is required"}), 400
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error":"Only PDF files are supported in Version 1"}), 400
    title = request.form.get("title", os.path.splitext(file.filename)[0]).strip()
    subject = request.form.get("subject", "").strip()
    if not title or not subject:
        return jsonify({"error":"Title and subject are required"}), 400
    document_id = str(uuid.uuid4())
    safe_name = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, f"{document_id}_{safe_name}")
    file.save(path)
    try:
        pages = extract_pdf(path)
        if not pages:
            raise ValueError("The PDF contains no extractable text. Scanned/handwritten OCR is future scope.")
        chunks = chunk_pages(pages)
        build_index(document_id, chunks)
    except Exception as exc:
        if os.path.exists(path):
            os.remove(path)
        return jsonify({"error": str(exc)}), 400
    user = get_user(request.user["sub"])
    data = {
        "id": document_id, "title": title, "subject": subject,
        "unit": request.form.get("unit", ""), "description": request.form.get("description", ""),
        "filename": safe_name, "stored_path": path, "uploaded_by": user["id"],
        "uploaded_by_name": user["name"], "created_at": datetime.now(timezone.utc).isoformat()
    }
    add_document(data)
    return jsonify({"document": get_document(document_id), "pages": len(pages), "chunks": len(chunks)})

@api.get("/documents/<doc_id>")
@require_auth()
def document(doc_id):
    doc = get_document(doc_id)
    if not doc:
        return jsonify({"error":"Document not found"}), 404
    return jsonify({"document": doc})

@api.post("/documents/<doc_id>/chat")
@require_auth()
def chat(doc_id):
    if not get_document(doc_id):
        return jsonify({"error":"Document not found"}), 404
    question = (request.get_json() or {}).get("question", "").strip()
    if not question:
        return jsonify({"error":"Question is required"}), 400
    chunks = retrieve(doc_id, question, 5)
    if not chunks:
        return jsonify({"error":"Document index is unavailable"}), 500
    try:
        answer = pdf_chat(question, chunks)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500
    add_message(doc_id, request.user["sub"], "user", question)
    add_message(doc_id, request.user["sub"], "assistant", answer)
    return jsonify({"answer": answer, "sources": [{"page": c["page"], "score": round(c["score"], 3)} for c in chunks]})

@api.get("/documents/<doc_id>/messages")
@require_auth()
def messages(doc_id):
    return jsonify({"messages": get_messages(doc_id, request.user["sub"])})

@api.post("/documents/<doc_id>/generate/<kind>")
@require_auth()
def generate_material(doc_id, kind):
    if kind not in ("summary", "exam", "flashcards", "quiz"):
        return jsonify({"error":"Unsupported material type"}), 400
    if not get_document(doc_id):
        return jsonify({"error":"Document not found"}), 404
    chunks = retrieve(doc_id, "important concepts definitions topics exam material", 12)
    if not chunks:
        return jsonify({"error":"Document index is unavailable"}), 500
    try:
        return jsonify({"type": kind, "result": study_material(kind, chunks)})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@api.post("/youtube/search")
@require_auth()
def youtube_search():
    query = (request.get_json() or {}).get("query", "").strip()
    if not query:
        return jsonify({"error":"Query is required"}), 400
    try:
        return jsonify({"videos": search(query), "searchConfigured": bool(os.getenv("YOUTUBE_API_KEY"))})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

@api.post("/youtube/analyze")
@require_auth()
def youtube_analyze():
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    action = data.get("action", "summary")
    if not url:
        return jsonify({"error":"YouTube URL is required"}), 400
    try:
        video_id, text = transcript(url)
        text = text[:30000]
        prompt = {
            "notes": "Create complete, structured study notes from this video transcript. Preserve the teacher's main ideas and examples.",
            "questions": "Explain the important concepts in this transcript and identify useful doubts a student may ask.",
            "summary": "Summarize this educational video into clear student-friendly study notes with headings, definitions and important points."
        }.get(action, "Summarize this educational video.")
        answer = generate(f"VIDEO TRANSCRIPT:\n{text}\n\nTASK:\n{prompt}", system="You are IntelliLearn AI analyzing an educational video transcript. Do not claim to have seen visuals that are absent from the transcript.")
        return jsonify({"videoId": video_id, "url": url, "action": action, "answer": answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400

@api.post("/youtube/ask")
@require_auth()
def youtube_ask():
    data = request.get_json() or {}
    url, question = data.get("url", ""), data.get("question", "").strip()
    if not url or not question:
        return jsonify({"error":"url and question are required"}), 400
    try:
        video_id, text = transcript(url)
        text = text[:30000]
        answer = generate(f"VIDEO TRANSCRIPT:\n{text}\n\nSTUDENT QUESTION:\n{question}", system="Answer using the supplied YouTube transcript. If the transcript does not contain enough information, say so. Do not invent visual details.")
        return jsonify({"videoId": video_id, "answer": answer})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 400
