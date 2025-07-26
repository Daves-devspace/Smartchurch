# test_pipeline.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Smartchurch.settings')
django.setup()


from scripture.summarization.summarizer import summarize
from scripture.ner.scripture_ner import detect_references

# Sample text for testing
sample_text = """
In John chapter 3 verse 16, the Bible says, 'For God so loved the world...'.
Romans 8:28 reminds us that all things work together for good.
"""

print("📝 Summary:")
print(summarize(sample_text))

print("\n🔍 Scripture Mentions Detected:")
print(detect_references(sample_text))
