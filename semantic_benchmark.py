import csv
import os
import random

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
)
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "data", "intents_v2.csv")
MODEL_NAME = "all-MiniLM-L6-v2"

random.seed(42)
np.random.seed(42)


def load_dataset():
    texts = []
    labels = []

    with open(DATASET_PATH, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            tag = row["tag"].strip()
            patterns = [
                p.strip()
                for p in row["patterns"].split("|")
                if p.strip()
            ]

            for pattern in patterns:
                texts.append(pattern)
                labels.append(tag)

    return texts, labels


def main():
    texts, labels = load_dataset()
    classes = sorted(set(labels))
    label_to_id = {label: i for i, label in enumerate(classes)}

    y = np.array([label_to_id[label] for label in labels])

    train_texts, test_texts, train_y, test_y = train_test_split(
        texts,
        y,
        test_size=0.20,
        random_state=42,
        stratify=y,
    )

    print("=" * 70)
    print("SEMANTIC MODEL BENCHMARK")
    print("=" * 70)
    print("Model:", MODEL_NAME)
    print("Total examples:", len(texts))
    print("Training examples:", len(train_texts))
    print("Test examples:", len(test_texts))
    print("Intents:", len(classes))
    print("=" * 70)

    encoder = SentenceTransformer(MODEL_NAME)

    train_embeddings = encoder.encode(
        train_texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    test_embeddings = encoder.encode(
        test_texts,
        normalize_embeddings=True,
        show_progress_bar=True,
    )

    prototypes = []

    for class_id in range(len(classes)):
        class_embeddings = train_embeddings[train_y == class_id]
        prototype = np.mean(class_embeddings, axis=0)
        prototype /= np.linalg.norm(prototype) + 1e-12
        prototypes.append(prototype)

    prototypes = np.asarray(prototypes)

    similarities = test_embeddings @ prototypes.T
    predicted = np.argmax(similarities, axis=1)

    accuracy = accuracy_score(test_y, predicted)
    weighted_precision, weighted_recall, weighted_f1, _ = (
        precision_recall_fscore_support(
            test_y,
            predicted,
            average="weighted",
            zero_division=0,
        )
    )

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(
            test_y,
            predicted,
            average="macro",
            zero_division=0,
        )
    )

    print("\n" + "=" * 70)
    print("SEMANTIC MODEL RESULTS")
    print("=" * 70)
    print(f"Accuracy           : {accuracy:.4f}")
    print(f"Weighted Precision : {weighted_precision:.4f}")
    print(f"Weighted Recall    : {weighted_recall:.4f}")
    print(f"Weighted F1        : {weighted_f1:.4f}")
    print(f"Macro Precision    : {macro_precision:.4f}")
    print(f"Macro Recall       : {macro_recall:.4f}")
    print(f"Macro F1           : {macro_f1:.4f}")
    print("=" * 70)

    print("\nCLASSIFICATION REPORT")
    print("-" * 70)
    print(
        classification_report(
            test_y,
            predicted,
            labels=range(len(classes)),
            target_names=classes,
            zero_division=0,
        )
    )

    output_path = os.path.join(
        BASE_DIR,
        "models",
        "semantic_benchmark.txt",
    )

    with open(output_path, "w", encoding="utf-8") as file:
        file.write("Sentence Transformer Semantic Intent Benchmark\n")
        file.write("=" * 60 + "\n\n")
        file.write(f"Model: {MODEL_NAME}\n")
        file.write(f"Total examples: {len(texts)}\n")
        file.write(f"Training examples: {len(train_texts)}\n")
        file.write(f"Test examples: {len(test_texts)}\n")
        file.write(f"Intents: {len(classes)}\n\n")
        file.write(f"Accuracy: {accuracy:.4f}\n")
        file.write(f"Weighted Precision: {weighted_precision:.4f}\n")
        file.write(f"Weighted Recall: {weighted_recall:.4f}\n")
        file.write(f"Weighted F1: {weighted_f1:.4f}\n")
        file.write(f"Macro Precision: {macro_precision:.4f}\n")
        file.write(f"Macro Recall: {macro_recall:.4f}\n")
        file.write(f"Macro F1: {macro_f1:.4f}\n\n")
        file.write(classification_report(
            test_y,
            predicted,
            labels=range(len(classes)),
            target_names=classes,
            zero_division=0,
        ))

    print("Saved:", output_path)


if __name__ == "__main__":
    main()
