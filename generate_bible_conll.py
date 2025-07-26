import random

books = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
    "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke",
    "John", "Acts", "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy",
    "Titus", "Philemon", "Hebrews", "James", "1 Peter", "2 Peter", "1 John", "2 John", "3 John",
    "Jude", "Revelation"
]

filler_sentences = [
    "I love reading", "My favorite verse is", "During prayer we mentioned", "Today's reading was from",
    "We discussed", "In our group study we read", "He quoted", "They referenced", "She reflected on",
    "The sermon covered"
]

def tokenize_and_label(sentence, book, chapter, verse):
    tokens = sentence.split()
    labels = ['O'] * len(tokens)

    try:
        # Find start index of scripture mention
        ref_parts = [book, str(chapter), ':', str(verse)]
        ref_str = f"{book} {chapter}:{verse}"
        ref_tokens = ref_str.split()
        for i in range(len(tokens) - len(ref_tokens) + 1):
            if tokens[i:i+len(ref_tokens)] == ref_tokens:
                labels[i] = 'B-REF'
                for j in range(1, len(ref_tokens)):
                    labels[i+j] = 'I-REF'
                break
    except Exception as e:
        print(f"Error labeling sentence: {sentence} -> {e}")
    return tokens, labels

def generate_conll_data(samples_per_book=10):
    lines = []
    for book in books:
        for _ in range(samples_per_book):
            chapter = random.randint(1, 50)
            verse = random.randint(1, 35)
            ref = f"{book} {chapter}:{verse}"
            filler = random.choice(filler_sentences)
            sentence = f"{filler} {ref} before dinner."
            tokens, labels = tokenize_and_label(sentence, book, chapter, verse)
            for tok, label in zip(tokens, labels):
                lines.append(f"{tok} {label}")
            lines.append("")  # Empty line to separate sentences
    return lines

if __name__ == "__main__":
    output_path = "generated_bible_train.conll"
    data = generate_conll_data(samples_per_book=15)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(data))
    print(f"Generated {output_path} with {len(data)} lines.")
