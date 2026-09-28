import csv
import os
import re

import nltk
from nltk.stem import WordNetLemmatizer


# ============================================================
# NLTK RESOURCE
# ============================================================

nltk.download("wordnet", quiet=True)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    BASE_DIR,
    "data",
    "intents_v2.csv"
)


# ============================================================
# LEMMATIZER
# ============================================================

lemmatizer = WordNetLemmatizer()


# ============================================================
# LOAD INTENTS
# ============================================================

intents = []

with open(
    DATA_PATH,
    newline="",
    encoding="utf-8"
) as csvfile:

    reader = csv.DictReader(csvfile)

    for row in reader:

        intents.append({
            "tag": row["tag"].strip(),

            "patterns": [
                pattern.strip()
                for pattern in row["patterns"].split("|")
                if pattern.strip()
            ],

            "responses": [
                response.strip()
                for response in row["responses"].split("|")
                if response.strip()
            ]
        })


# ============================================================
# NLP DATA STRUCTURES
# ============================================================

words = []
classes = []
documents = []


# ============================================================
# TOKENIZATION
# ============================================================

for intent in intents:

    tag = intent["tag"]

    if tag not in classes:
        classes.append(tag)

    for pattern in intent["patterns"]:

        # Convert sentence to lowercase
        pattern = pattern.lower()

        # Extract words
        word_list = re.findall(
            r"\b\w+\b",
            pattern
        )

        # Lemmatize words
        word_list = [
            lemmatizer.lemmatize(word)
            for word in word_list
        ]

        words.extend(word_list)

        documents.append(
            (word_list, tag)
        )


# ============================================================
# CLEAN VOCABULARY
# ============================================================

words = sorted(
    set(words)
)

classes = sorted(
    set(classes)
)


# ============================================================
# INFORMATION
# ============================================================

print("=" * 60)
print("INTENT DATASET LOADED")
print("=" * 60)

print(
    f"Dataset: {DATA_PATH}"
)

print(
    f"Intents: {len(classes)}"
)

print(
    f"Training patterns: {len(documents)}"
)

print(
    f"Vocabulary size: {len(words)}"
)

print("=" * 60)