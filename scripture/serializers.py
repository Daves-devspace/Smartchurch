# scripture/serializers.py
from rest_framework import serializers
from .models import ScriptureReferenceLog

class ScriptureReferenceSerializer(serializers.Serializer):
    book = serializers.CharField()
    chapter = serializers.CharField()
    verse = serializers.CharField()
    confidence = serializers.FloatField()
    source = serializers.CharField()

class ScriptureReferenceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScriptureReferenceLog
        fields = '__all__'