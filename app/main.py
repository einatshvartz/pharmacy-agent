from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.agent import stream_agent_reply
import logging

app = FastAPI(title="Pharmacy Agent")
logging.basicConfig(level=logging.INFO)

@app.get("/health")
def health():
    return {"status": "ok"}


class ChatRequest(BaseModel):
    user_id: str
    message: str


@app.post("/chat")
def chat(req: ChatRequest):
    # Stateless: no conversation state is stored server-side
    return StreamingResponse(
        stream_agent_reply(req.user_id, req.message),
        media_type="text/plain"
    )
