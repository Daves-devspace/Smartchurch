# Scripture Detection API & NER Fine-Tuning Guide

#This document covers:
#1. **Django CBV + Serializer** for `/api/detect-references/` including analytics logging.
#2. **Step-by-step fine-tuning** of your DistilBERT NER model on annotated scripture data.


## 1. Django API: CBV, Serializer, Model & URL

### 1.1 Define the Analytics Model

# scripture/models.py
from django.db import models

class ScriptureReferenceLog(models.Model):
    book = models.CharField(max_length=50)
    chapter = models.CharField(max_length=10)
    verse = models.CharField(max_length=20)
    source = models.CharField(max_length=10)      # 'ml' or 'regex'
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book} {self.chapter}:{self.verse} ({self.source})"