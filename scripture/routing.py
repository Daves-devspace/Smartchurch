from django.urls import re_path
from scripture.transcription import consumers

websocket_urlpatterns = [
    re_path(r"ws/verses/$", consumers.LiveVerseConsumer.as_asgi()),
    re_path(r"ws/transcription/$", consumers.TranscriptionConsumer.as_asgi()),  # 👈 ADD THIS LINE
]
