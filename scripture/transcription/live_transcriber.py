# live_transcriber.py
import os
import threading
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smartchurch.settings')
django.setup()

from scripture.transcription.overlay_engine import LiveVerseOverlayEngine

engine = None
thread = None

def start_in_thread(model_size="small", device="cpu"):
    global engine, thread

    if engine is None:
        engine = LiveVerseOverlayEngine(model_size=model_size, device=device)

    if thread is None or not thread.is_alive():
        thread = threading.Thread(target=engine.start)
        thread.daemon = True
        thread.start()
        print("✅ Live transcription started.")

def stop_live_transcription():
    global engine
    if engine:
        engine.stop()
        print("🛑 Live transcription stopped.")
        engine = None
