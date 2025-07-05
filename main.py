from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from googletrans import Translator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

translator = Translator()

class ChatRequest(BaseModel):
    text: str

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    user_text_ja = req.text

    # 日本語 → 英語翻訳
    user_text_en = translator.translate(user_text_ja, src="ja", dest="en").text

    # 「回答だけを簡潔に」の指示を強化したプロンプト
    prompt = (
        "Please answer the question below with a short, direct sentence. "
        "Do NOT include any extra explanation, questions, or follow-ups.\n"
        "You don't have to answer anything other than the question.\n"
        f"Question: {user_text_en}"
    )

    payload = {
        "prompt": prompt,
        "n_predict": 120
    }

    try:
        response = requests.post("http://127.0.0.1:8080/completion", json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="モデルサーバ呼び出しエラー")

    result = response.json()
    output_en = result.get("content", "").strip()

    # 英語 → 日本語翻訳
    output_ja = translator.translate(output_en, src="en", dest="ja").text

    return {"answer": output_ja}
