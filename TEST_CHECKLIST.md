# Manual Test Checklist

After installation, run the backend and frontend and verify these in order.

## A. Backend
- [ ] `GET /api/health` returns `{"status":"ok"...}`
- [ ] Register student succeeds
- [ ] Register faculty succeeds
- [ ] Login succeeds
- [ ] Invalid password returns an error

## B. Faculty
- [ ] Faculty can open Faculty Upload
- [ ] Student cannot access Faculty Upload
- [ ] PDF upload accepts a text-based PDF
- [ ] PDF upload rejects non-PDF files
- [ ] Upload response reports page/chunk counts

## C. Student PDF workflow
- [ ] Student sees uploaded PDF in Academic Library
- [ ] Student opens the PDF study panel
- [ ] Student asks a question
- [ ] Answer includes source page indicators
- [ ] Summary generates
- [ ] 10-mark answer generates
- [ ] Flashcards generate as cards
- [ ] Quiz generates with four options per question

## D. YouTube
- [ ] Search works when `YOUTUBE_API_KEY` is configured
- [ ] Selecting a result fills the URL
- [ ] A URL with accessible transcript can be analyzed
- [ ] Complete Notes generates
- [ ] Key Concepts generates
- [ ] A doubt can be asked from the transcript
- [ ] A video without accessible transcript gives a clear error

## E. Failure cases
- [ ] Missing GROQ key gives a readable configuration error
- [ ] Empty question is rejected
- [ ] Missing PDF text gives a clear OCR/future-scope message
- [ ] Oversized upload is rejected
