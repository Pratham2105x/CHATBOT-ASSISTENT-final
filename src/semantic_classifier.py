import csv
import os
from collections import defaultdict

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASET_PATH = os.path.join(BASE_DIR, "data", "intents_v2.csv")


class SemanticIntentClassifier:
    """Semantic intent classifier using Sentence Transformers.

    Each intent is represented by the mean embedding of its training
    patterns. A new query is embedded and compared with every intent
    prototype using cosine similarity.
    """

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.encoder = SentenceTransformer(model_name)
        self.classes = []
        self.prototypes = None
        self._load_dataset()
        self._build_prototypes()

    def _load_dataset(self):
        grouped = defaultdict(list)

        with open(DATASET_PATH, newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                tag = row["tag"].strip()
                patterns = [
                    p.strip()
                    for p in row["patterns"].split("|")
                    if p.strip()
                ]
                grouped[tag].extend(patterns)

        self.classes = sorted(grouped.keys())
        self.patterns_by_class = grouped

    def _build_prototypes(self):
        prototypes = []

        for intent in self.classes:
            embeddings = self.encoder.encode(
                self.patterns_by_class[intent],
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            prototype = np.mean(embeddings, axis=0)
            prototype /= np.linalg.norm(prototype) + 1e-12
            prototypes.append(prototype)

        self.prototypes = np.asarray(prototypes, dtype=np.float32)

    def predict(self, text, top_k=3):
        embedding = self.encoder.encode(
            [text],
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        similarities = cosine_similarity(
            embedding,
            self.prototypes,
        )[0]

        ranking = np.argsort(similarities)[::-1][:top_k]

        results = []
        for index in ranking:
            results.append(
                {
                    "intent": self.classes[int(index)],
                    "confidence": float(similarities[index]),
                }
            )

        return results


if __name__ == "__main__":
    classifier = SemanticIntentClassifier()

    print("=" * 60)
    print("SEMANTIC INTENT CLASSIFIER")
    print("=" * 60)
    print("Model:", classifier.model_name)
    print("Intents:", len(classifier.classes))
    print("Embedding dimension:", classifier.prototypes.shape[1])
    print("=" * 60)

    examples = [
        "Do you have any discounts?",
        "Where is my package?",
        "Can I return this item?",
        "What payment methods do you accept?",
    ]

    for text in examples:
        print("\nQuestion:", text)
        for result in classifier.predict(text):
            print(
                f"  {result['intent']:<25} "
                f"{result['confidence']:.4f}"
            )
