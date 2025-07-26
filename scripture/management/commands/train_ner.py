# # scripture/management/commands/train_ner.py

# import os
# import logging
# from django.core.management.base import BaseCommand
# from datasets import load_dataset, ClassLabel, Features, Sequence, Value
# from transformers import (
#     AutoTokenizer,
#     AutoModelForTokenClassification,
#     TrainingArguments,
#     Trainer
# )
# from seqeval.metrics import accuracy_score, f1_score
# from huggingface_hub import HfApi, upload_folder
# from dotenv import load_dotenv

# # Load .env file for HF auth
# load_dotenv()
# HF_TOKEN = os.environ.get("HF_HUB_TOKEN")
# if not HF_TOKEN:
#     raise RuntimeError("Missing HF_HUB_TOKEN in environment")

# # Logging
# logger = logging.getLogger(__name__)

# class Command(BaseCommand):
#     help = "Fine-tune DistilBERT for scripture NER and optionally push to HF Hub"

#     def add_arguments(self, parser):
#         parser.add_argument('--push', action='store_true', help="Push model to Hugging Face Hub")

#     def handle(self, *args, **options):
#         MODEL_NAME = 'distilbert-base-uncased'
#         OUTPUT_DIR = 'output/distil-scripture-ner'
#         TAGS = ['O', 'B-BOOK', 'I-BOOK', 'B-CHAPTER', 'I-CHAPTER', 'B-VERSE', 'I-VERSE']
#         tag2id = {tag: i for i, tag in enumerate(TAGS)}
#         id2tag = {i: tag for tag, i in tag2id.items()}

#         # Step 1. Load & parse raw CoNLL as text
#         self.stdout.write("🔍 Loading and parsing CoNLL data…")
#         datasets = load_dataset(
#             'text',
#             data_files={
#                 'train': 'data/train.conll',
#                 'validation': 'data/val.conll'
#             }
#         )

#         def parse_conll(example):
#             lines = example["text"].split("\n")
#             tokens, tags = [], []
#             for line in lines:
#                 if line.strip() == "":
#                     continue
#                 parts = line.strip().split()
#                 if len(parts) >= 2:
#                     tokens.append(parts[0])
#                     tags.append(tag2id.get(parts[-1], 0))  # default to 'O' if unknown
#             return {"tokens": tokens, "ner_tags": tags}

#         datasets = datasets.map(parse_conll)

#         # Step 2. Tokenizer & Model
#         self.stdout.write(f"🔧 Loading tokenizer and model from '{MODEL_NAME}'")
#         tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#         model = AutoModelForTokenClassification.from_pretrained(
#             MODEL_NAME,
#             num_labels=len(TAGS),
#             id2label=id2tag,
#             label2id=tag2id
#         )

#         # Step 3. Tokenization + alignment
#         def tokenize_and_align_labels(examples):
#             tokenized = tokenizer(
#                 examples['tokens'],
#                 is_split_into_words=True,
#                 truncation=True,
#                 padding='max_length'
#             )
#             labels = []
#             for i, label_seq in enumerate(examples['ner_tags']):
#                 word_ids = tokenized.word_ids(batch_index=i)
#                 label_ids = []
#                 prev_word_idx = None
#                 for word_idx in word_ids:
#                     if word_idx is None:
#                         label_ids.append(-100)
#                     elif word_idx != prev_word_idx:
#                         label_ids.append(label_seq[word_idx])
#                     else:
#                         curr = label_seq[word_idx]
#                         label_ids.append(curr if curr % 2 else curr + 1)
#                     prev_word_idx = word_idx
#                 labels.append(label_ids)
#             tokenized["labels"] = labels
#             return tokenized

#         self.stdout.write("🧼 Tokenizing and aligning labels…")
#         tokenized = datasets.map(
#             tokenize_and_align_labels,
#             batched=True,
#             remove_columns=datasets["train"].column_names
#         )

#         # Step 4. Training arguments
#         self.stdout.write("⚙️ Configuring training arguments…")
#         args = TrainingArguments(
#             output_dir=OUTPUT_DIR,
#             evaluation_strategy='steps',
#             per_device_train_batch_size=16,
#             per_device_eval_batch_size=16,
#             num_train_epochs=3,
#             save_steps=500,
#             eval_steps=500,
#             logging_steps=100,
#             logging_dir=os.path.join(OUTPUT_DIR, 'logs'),
#         )

#         # Step 5. Metrics
#         def compute_metrics(p):
#             preds = p.predictions.argmax(axis=-1)
#             labels = p.label_ids
#             true_labels = [
#                 [id2tag[l] for l in label_seq if l != -100]
#                 for label_seq in labels
#             ]
#             true_preds = [
#                 [id2tag[p_i] for p_i, l in zip(pred_seq, label_seq) if l != -100]
#                 for pred_seq, label_seq in zip(preds, labels)
#             ]
#             return {
#                 'f1': f1_score(true_labels, true_preds),
#                 'accuracy': accuracy_score(true_labels, true_preds)
#             }

#         # Step 6. Train
#         self.stdout.write("🚀 Training model…")
#         trainer = Trainer(
#             model=model,
#             args=args,
#             train_dataset=tokenized['train'],
#             eval_dataset=tokenized['validation'],
#             compute_metrics=compute_metrics
#         )

#         trainer.train()
#         trainer.save_model(OUTPUT_DIR)
#         self.stdout.write(self.style.SUCCESS(f"✅ Model saved to {OUTPUT_DIR}"))

#         # Step 7. Optional: Push to HF Hub
#         if options['push']:
#             self.stdout.write("📤 Uploading to Hugging Face Hub…")
#             api = HfApi()
#             api.upload_folder(
#                 folder_path=OUTPUT_DIR,
#                 repo_id="Liorixdigital/distilbert-scripture-ner",
#                 repo_type="model",
#                 path_in_repo="",
#                 token=HF_TOKEN
#             )
#             self.stdout.write(self.style.SUCCESS(
#                 "🚀 Model pushed: https://huggingface.co/Liorixdigital/distilbert-scripture-ner"
#             ))
