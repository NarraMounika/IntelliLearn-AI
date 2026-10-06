# Start Here

## 1. Open the folder
Open `IntelliLearn-AI` in VS Code.

## 2. Backend
Open a terminal:

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set `GROQ_API_KEY` and a strong `JWT_SECRET`.

Then:

```powershell
python run.py
```

## 3. Frontend
Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## 4. Demo order
1. Register as Faculty.
2. Upload a text-based academic PDF.
3. Register/login as Student.
4. Open the PDF.
5. Ask a question.
6. Generate summary, flashcards, quiz and 10-mark answer.
7. Open YouTube Learning.
8. Paste a YouTube educational URL with English captions.
9. Generate notes or ask a doubt.

## 5. If something fails
- `GROQ_API_KEY` missing -> AI generation will fail.
- First PDF indexing is slow -> the embedding model is downloaded the first time.
- YouTube search empty -> add `YOUTUBE_API_KEY`.
- YouTube analysis says no transcript -> choose a video with captions/transcript.
- Scanned handwritten PDF -> OCR is not included in Version 1.
