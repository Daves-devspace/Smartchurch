# Smartchurch/routing.py
from django.urls import re_path
from scripture.transcription.consumers import TranscriptionConsumer, LiveVerseConsumer

websocket_urlpatterns = [
    re_path(r"ws/transcription/$", TranscriptionConsumer.as_asgi()),
    re_path(r"ws/verses/$",        LiveVerseConsumer.as_asgi()),
]
