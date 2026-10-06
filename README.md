# IntelliLearn AI

An AI-powered academic learning assistant for faculty-provided PDFs/notes and educational YouTube videos.

## Version 1 features
- Student and faculty authentication with roles
- Faculty PDF upload with title, subject, unit and description
- Student resource library
- PDF text extraction
- Per-document FAISS vector index with Sentence Transformers embeddings
- RAG chat grounded in the selected academic document
- AI summary, exam-style answer, flashcards and MCQ quiz generation
- YouTube URL loading and transcript-based analysis
- YouTube notes, summary and question answering
- Clean React/Vite frontend and Flask API

## Architecture

React/Vite -> Flask REST API -> Services
                         |-> SQLite (local development)
                         |-> Local uploads
                         |-> FAISS vector indexes
                         |-> Sentence Transformers embeddings
                         |-> Groq LLM
                         |-> YouTube Transcript API

## Why this version is intentionally smaller
The uploaded reference projects contain several enterprise features (Celery/Redis, graph RAG, BM25 reranking, OCR, PostgreSQL, Docker, etc.). They are useful references but would make a first student implementation harder to run and explain. This project keeps the core RAG + learning workflow and leaves those features as future scope.

## Requirements
- Python 3.10+
- Node.js 18+ (20 LTS is recommended)
- A Groq API key for AI generation
- Optional YouTube Data API key for video search

## Backend setup

```bash
cd backend
python -m venv .venv
# Windows PowerShell
.venv\\Scripts\\Activate.ps1
# Windows CMD
# .venv\\Scripts\\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend runs at `http://localhost:5000`.

## Frontend setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Environment variables

See `backend/.env.example`.

At minimum set:

```env
GROQ_API_KEY=your_key
JWT_SECRET=change_this_to_a_long_random_secret
```

If you want YouTube topic search, also set:

```env
YOUTUBE_API_KEY=your_youtube_data_api_key
```

If YouTube search is unavailable, users can still paste a YouTube URL that has an accessible transcript.

## Demo accounts
There is no hard-coded account. Register two users:
- one with role `faculty`
- one with role `student`

In a real deployment, faculty role assignment should be restricted by an administrator or college policy. For this student project, role selection is kept simple for local demonstration.

## Important RAG behavior
The PDF chat prompt instructs the model to use the selected document context and clearly state when the document does not contain enough information. This is preferable to silently mixing unrelated knowledge into an academic answer.

## Source/reference note
This implementation is an original integration designed for IntelliLearn AI. The four uploaded repositories were inspected for architecture and feature ideas. Their source code was not bundled into this project. See `REFERENCE_NOTES.md` for the mapping and the original repository licenses.

## Verification

Python source files have been syntax-checked in the prepared project. The build is designed for Vite/React, but dependency installation was not completed in the packaging environment, so run `npm install` and `npm run build` locally as the final frontend verification step. See `TEST_CHECKLIST.md`.
