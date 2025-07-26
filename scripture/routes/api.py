# scripture/routes/api.py
from fastapi import APIRouter
from scripture.transcription.live_transcriber import start_in_thread, stop_live_transcription

router = APIRouter()

@router.post("/start-stream")
async def start_stream():
    start_in_thread()
    return {"status": "started"}

@router.post("/stop-stream")
async def stop_stream():
    stop_live_transcription()
    return {"status": "stopped"}

@router.get("/ping")
def ping():
    return {"message": "pong"}





