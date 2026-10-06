# IntelliLearn AI - Feature Map

| IntelliLearn feature | Implementation | Reference inspiration inspected |
|---|---|---|
| Student/faculty login | `backend/app/auth.py`, `db.py`, auth pages in `frontend/src/main.jsx` | StudyMatePlus authentication structure |
| Faculty PDF upload | `/api/documents/upload` | StudyMatePlus resource/upload flow + CognitiveSB file loading |
| PDF extraction | `backend/app/services/documents.py` | CognitiveSB file loader + PDF Assistant RAG document pipeline |
| Chunking | `chunk_pages()` | CognitiveSB chunker |
| Embeddings | Sentence Transformers | CognitiveSB embedder / PDF Assistant RAG embeddings |
| Vector retrieval | FAISS per document | CognitiveSB vector store |
| PDF chat | `/api/documents/:id/chat` | CognitiveSB RAG workflow |
| Summary | `/generate/summary` | CognitiveSB notes + PDFQuizzer summarization idea |
| Exam answer | `/generate/exam` | IntelliLearn-specific prompt built around academic exam use |
| Flashcards | `/generate/flashcards` | CognitiveSB flashcard workflow |
| Quiz | `/generate/quiz` | PDFQuizzer MCQ workflow + CognitiveSB quiz workflow |
| YouTube search | `/api/youtube/search` | CognitiveSB YouTube workflow; YouTube Data API |
| YouTube transcript | `youtube.py` | CognitiveSB YouTube loader |
| YouTube notes/Q&A | `/youtube/analyze`, `/youtube/ask` | CognitiveSB transcript + RAG idea |

## Intentionally not copied
No source file from the supplied repositories was bundled as a dependency. The IntelliLearn implementation is a clean project built around the useful architectural ideas discovered during inspection.

## Future extensions
- MongoDB Atlas instead of SQLite
- OCR for scanned/handwritten notes
- hybrid BM25 + vector retrieval
- reranking
- graph RAG
- Celery/Redis background processing
- PYQ topic-frequency analysis
- personalized study planner
- progress tracking
- spaced repetition scheduling
