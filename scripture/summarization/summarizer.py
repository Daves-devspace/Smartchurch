from transformers import pipeline

# load once
summarizer = pipeline(
    "summarization",
    model="facebook/bart-large-cnn",
    device="cpu"
)

def summarize(text: str, min_length=30, max_length=100) -> str:
    words = text.split()
    if len(words) < 5:
        return "Not enough content to summarize."
    length = len(words)
    minl = min(min_length, length)
    maxl = min(max_length, length+10)
    return summarizer(text, min_length=minl, max_length=maxl, do_sample=False)[0]["summary_text"].strip()