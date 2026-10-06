import os, json
from groq import Groq

def generate(prompt, system=None, json_mode=False):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not configured. Add it to backend/.env.")
    kwargs = {
        "model": os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
        "temperature": 0.2,
        "max_tokens": 3500,
    }
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    result = Groq(api_key=key).chat.completions.create(messages=messages, **kwargs)
    return result.choices[0].message.content

def context_text(chunks):
    return "\n\n".join(f"[Page {c['page']}] {c['text']}" for c in chunks)

def pdf_chat(question, chunks):
    system = """You are IntelliLearn AI, an academic assistant. Answer using the supplied document context first. Do not invent facts that are not supported by the context. If the document does not contain enough information, say so clearly. Use simple student-friendly language. For exam answers, organize the answer with headings and points."""
    return generate(f"DOCUMENT CONTEXT:\n{context_text(chunks)}\n\nSTUDENT QUESTION:\n{question}", system=system)

def study_material(kind, chunks):
    prompts = {
        "summary": "Create a clear study summary from the document. Include major concepts, definitions and important points. Do not add unsupported facts.",
        "exam": "Create a 10-mark exam-style answer from the document. Use a short introduction, headings, numbered points and a conclusion where useful.",
        "flashcards": "Create 10 useful revision flashcards. Return JSON with a flashcards array. Each item must have front and back.",
        "quiz": "Create 8 MCQs for revision. Return JSON with a questions array. Each item must have question, options (exactly 4 strings), answer (the correct option text), and explanation."
    }
    result = generate(
        f"DOCUMENT CONTEXT:\n{context_text(chunks)}\n\nTASK:\n{prompts[kind]}",
        system="You create accurate academic study material grounded in the supplied document.",
        json_mode=kind in ("flashcards", "quiz")
    )
    if kind in ("flashcards", "quiz"):
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"raw": result}
    return result
