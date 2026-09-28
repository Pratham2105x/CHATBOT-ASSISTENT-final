import os
import re
import random

import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
)

from src.preprocess import intents


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(42)
np.random.seed(42)


# ============================================================
# BUILD DATASET
# ============================================================

texts = []
labels = []

for intent in intents:

    tag = intent["tag"]

    for pattern in intent["patterns"]:

        text = re.sub(
            r"\s+",
            " ",
            pattern.strip().lower()
        )

        if text:

            texts.append(text)
            labels.append(tag)


print("=" * 70)
print("NLP MODEL BENCHMARK")
print("=" * 70)

print(f"Total examples : {len(texts)}")
print(f"Total intents  : {len(set(labels))}")

print("=" * 70)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(

    texts,
    labels,

    test_size=0.20,

    random_state=42,

    stratify=labels
)


print(f"Training examples: {len(X_train)}")
print(f"Test examples    : {len(X_test)}")

print("=" * 70)


# ============================================================
# TF-IDF
# ============================================================

vectorizer = TfidfVectorizer(

    ngram_range=(1, 2),

    min_df=1,

    sublinear_tf=True,

    max_features=5000
)


X_train_tfidf = vectorizer.fit_transform(
    X_train
)

X_test_tfidf = vectorizer.transform(
    X_test
)


# ============================================================
# EVALUATION FUNCTION
# ============================================================

results = []


def evaluate_model(
    name,
    model
):

    model.fit(
        X_train_tfidf,
        y_train
    )

    predictions = model.predict(
        X_test_tfidf
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision, recall, f1, _ = (
        precision_recall_fscore_support(

            y_test,

            predictions,

            average="weighted",

            zero_division=0
        )
    )

    macro_precision, macro_recall, macro_f1, _ = (
        precision_recall_fscore_support(

            y_test,

            predictions,

            average="macro",

            zero_division=0
        )
    )

    results.append({

        "Model": name,

        "Accuracy": accuracy,

        "Weighted Precision": precision,

        "Weighted Recall": recall,

        "Weighted F1": f1,

        "Macro F1": macro_f1
    })


# ============================================================
# MODEL 1 — LOGISTIC REGRESSION
# ============================================================

logistic_model = LogisticRegression(

    max_iter=2000,

    C=2.0,

    class_weight="balanced",

    random_state=42
)


evaluate_model(
    "TF-IDF + Logistic Regression",
    logistic_model
)


# ============================================================
# MODEL 2 — LINEAR SVM
# ============================================================

svm_model = LinearSVC(

    C=1.5,

    class_weight="balanced",

    random_state=42
)


evaluate_model(
    "TF-IDF + Linear SVM",
    svm_model
)


# ============================================================
# RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)


results_df = results_df.sort_values(
    by="Weighted F1",
    ascending=False
)


print()
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)

print("=" * 70)


# ============================================================
# SAVE RESULTS
# ============================================================

os.makedirs(
    "models",
    exist_ok=True
)


results_df.to_csv(
    "models/model_comparison.csv",
    index=False
)


print(
    "\nSaved: models/model_comparison.csv"
)
