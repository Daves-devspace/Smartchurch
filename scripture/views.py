# sequenceDiagram
#     participant React as Frontend
#     participant Django as API
#     participant NER as ner.py
#     participant FTS as RetrievalService

#     React->>Django: POST /api/scripture/detect-references\n{ "text": "...John 3:16 and Genesis 1:1..." }
#     Django->>NER: detect_references(text)
#     NER-->>Django: [ {book,chapter,verse,confidence,source}, ... ]
#     Django->>FTS: get_exact_verses(book,chapter,verse) × n
#     FTS-->>Django: [ {book,chapter,verse,text}, ... ] × n
#     Django-->>Django: log each ref to ScriptureReferenceLog
#     Django-->>React: HTTP 200\n{ "references": [ {book,chapter,verse,text,confidence,source}, ... ] }
#     React-->>React: display <VerseOverlay> and update <VerseHistory>




from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .ner.scripture_ner import detect_references
from .retrieval.verse_retriever import get_exact_verses

from rest_framework.views import APIView
from rest_framework.response import Response
from .speech_utils import process_audio_file

# scripture/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .ner.scripture_ner import detect_references
from .models import ScriptureReferenceLog
from .serializers import ScriptureReferenceSerializer

class DetectReferencesAPIView(APIView):
    """
    POST {'text': string} → {'references': [...]}
    Detects scripture references and logs them for analytics.
    """
    def post(self, request):
        text = request.data.get('text', '')
        if not text:
            return Response({'error': 'No text provided'}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Detect references
        refs = detect_references(text)

        # 2. Serialize results
        ref_serializer = ScriptureReferenceSerializer(refs, many=True)

        # 3. Log analytics entries
        for ref in refs:
            ScriptureReferenceLog.objects.create(
                book=ref['book'],
                chapter=ref['chapter'],
                verse=ref['verse'],
                source=ref['source'],
                confidence=ref['confidence']
            )

        return Response({'references': ref_serializer.data}, status=status.HTTP_200_OK)
    
    




class SpeechProcessAPIView(APIView):
    """
    Accepts multipart/form-data with an 'audio' file.
    Returns transcript, scripture refs, and summary.
    """
    def post(self, request):
        audio = request.FILES.get("audio")
        if not audio:
            return Response({"error": "No audio file uploaded"}, status=400)

        # save the uploaded file temporarily
        tmp_path = "/tmp/uploaded.wav"
        with open(tmp_path, "wb") as f:
            for chunk in audio.chunks():
                f.write(chunk)

        result = process_audio_file(tmp_path)
        return Response(result)

@api_view(["POST"])
def detect_reference(request):
    text = request.data.get("text", "")
    refs = detect_references(text)
    return Response({"references": refs})

@api_view(["POST"])
def get_verse(request):
    book = request.data["book"]
    chapter = request.data["chapter"]
    verse = request.data["verse"]
    verses = get_exact_verses(book, chapter, verse)
    return Response({"verses": verses})