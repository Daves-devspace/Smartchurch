from django.urls import path
from . import views
from .views import DetectReferencesAPIView, SpeechProcessAPIView

urlpatterns = [
    path('detect-references/', DetectReferencesAPIView.as_view(), name='detect-references'),
    path("process-speech/", SpeechProcessAPIView.as_view(), name="process-speech"),
    
    path("detect-reference/", views.detect_reference),
    path("get-verse/", views.get_verse),
    
    
]
