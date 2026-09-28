import os
import random
import json

import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Dropout, Input
from keras.optimizers import SGD

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
)

from src.preprocess import (
    words,
    classes,
    documents,
    lemmatizer,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# REPRODUCIBILITY
# ============================================================

random.seed(42)
np.random.seed(42)


# ============================================================
# DATASET INFORMATION
# ============================================================

print("=" * 60)
print("TRAINING CHATBOT MODEL")
print("=" * 60)

print(
    f"Total examples : {len(documents)}"
)

print(
    f"Vocabulary     : {len(words)}"
)

print(
    f"Intents        : {len(classes)}"
)

print("=" * 60)


# ============================================================
# CREATE BAG OF WORDS
# ============================================================

training = []

output_empty = [
    0
] * len(classes)


for doc in documents:

    bag = []

    word_patterns = doc[0]


    word_patterns = [
        lemmatizer.lemmatize(
            word.lower()
        )
        for word in word_patterns
    ]


    for word in words:

        if word in word_patterns:

            bag.append(1)

        else:

            bag.append(0)


    output_row = list(
        output_empty
    )


    output_row[
        classes.index(
            doc[1]
        )
    ] = 1


    training.append(
        [
            bag,
            output_row
        ]
    )


# ============================================================
# SHUFFLE
# ============================================================

random.shuffle(
    training
)


# ============================================================
# NUMPY ARRAYS
# ============================================================

train_x = np.array(
    [
        item[0]
        for item in training
    ],
    dtype=np.float32
)


train_y = np.array(
    [
        item[1]
        for item in training
    ],
    dtype=np.float32
)


labels = np.argmax(
    train_y,
    axis=1
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

(
    train_x,
    test_x,
    train_y,
    test_y,
    train_labels,
    test_labels
) = train_test_split(
    train_x,
    train_y,
    labels,
    test_size=0.20,
    random_state=42,
    stratify=labels
)


print(
    f"Training       : {len(train_x)}"
)

print(
    f"Test           : {len(test_x)}"
)

print(
    f"Input features : {train_x.shape[1]}"
)

print("=" * 60)


# ============================================================
# MODEL
# ============================================================

model = Sequential(
    [

        Input(
            shape=(
                train_x.shape[1],
            )
        ),

        Dense(
            128,
            activation="relu"
        ),

        Dropout(
            0.4
        ),

        Dense(
            64,
            activation="relu"
        ),

        Dropout(
            0.3
        ),

        Dense(
            len(classes),
            activation="softmax"
        ),

    ]
)


# ============================================================
# OPTIMIZER
# ============================================================

optimizer = SGD(
    learning_rate=0.01,
    momentum=0.9,
    nesterov=True
)


model.compile(
    loss="categorical_crossentropy",
    optimizer=optimizer,
    metrics=[
        "accuracy"
    ]
)


# ============================================================
# TRAIN
# ============================================================

model.fit(
    train_x,
    train_y,
    epochs=150,
    batch_size=16,
    verbose=1
)


# ============================================================
# EVALUATION
# ============================================================

probabilities = model.predict(
    test_x,
    verbose=0
)


predicted_labels = np.argmax(
    probabilities,
    axis=1
)


accuracy = accuracy_score(
    test_labels,
    predicted_labels
)


weighted_precision, weighted_recall, weighted_f1, _ = (
    precision_recall_fscore_support(
        test_labels,
        predicted_labels,
        average="weighted",
        zero_division=0
    )
)


macro_precision, macro_recall, macro_f1, _ = (
    precision_recall_fscore_support(
        test_labels,
        predicted_labels,
        average="macro",
        zero_division=0
    )
)


print()
print("=" * 60)
print("MODEL EVALUATION")
print("=" * 60)

print(
    f"Accuracy          : {accuracy:.4f}"
)

print(
    f"Weighted Precision : {weighted_precision:.4f}"
)

print(
    f"Weighted Recall    : {weighted_recall:.4f}"
)

print(
    f"Weighted F1        : {weighted_f1:.4f}"
)

print(
    f"Macro Precision    : {macro_precision:.4f}"
)

print(
    f"Macro Recall       : {macro_recall:.4f}"
)

print(
    f"Macro F1           : {macro_f1:.4f}"
)

print("=" * 60)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

report = classification_report(
    test_labels,
    predicted_labels,
    labels=range(
        len(classes)
    ),
    target_names=classes,
    zero_division=0
)


print()
print("CLASSIFICATION REPORT")
print("-" * 60)
print(report)


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    test_labels,
    predicted_labels,
    labels=range(
        len(classes)
    )
)


# ============================================================
# SAVE MODEL
# ============================================================

model_path = os.path.join(
    MODEL_DIR,
    "chatbot_model.h5"
)


model.save(
    model_path
)


# ============================================================
# SAVE VOCABULARY
# ============================================================

words_path = os.path.join(
    MODEL_DIR,
    "words.json"
)


with open(
    words_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        words,
        file,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# SAVE CLASSES
# ============================================================

classes_path = os.path.join(
    MODEL_DIR,
    "classes.json"
)


with open(
    classes_path,
    "w",
    encoding="utf-8"
) as file:

    json.dump(
        classes,
        file,
        ensure_ascii=False,
        indent=2
    )


# ============================================================
# SAVE EVALUATION
# ============================================================

evaluation_path = os.path.join(
    MODEL_DIR,
    "evaluation.txt"
)


with open(
    evaluation_path,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "ShopBot Intent Classification Evaluation\n"
    )

    file.write(
        "=" * 55
        + "\n\n"
    )

    file.write(
        f"Intents: {len(classes)}\n"
    )

    file.write(
        f"Vocabulary size: {len(words)}\n"
    )

    file.write(
        f"Total examples: {len(documents)}\n"
    )

    file.write(
        f"Training examples: {len(train_x)}\n"
    )

    file.write(
        f"Test examples: {len(test_x)}\n\n"
    )

    file.write(
        f"Accuracy: {accuracy:.4f}\n"
    )

    file.write(
        f"Weighted Precision: {weighted_precision:.4f}\n"
    )

    file.write(
        f"Weighted Recall: {weighted_recall:.4f}\n"
    )

    file.write(
        f"Weighted F1: {weighted_f1:.4f}\n"
    )

    file.write(
        f"Macro Precision: {macro_precision:.4f}\n"
    )

    file.write(
        f"Macro Recall: {macro_recall:.4f}\n"
    )

    file.write(
        f"Macro F1: {macro_f1:.4f}\n\n"
    )

    file.write(
        "Classification Report\n"
    )

    file.write(
        "-" * 55
        + "\n"
    )

    file.write(
        report
    )


# ============================================================
# SAVE CONFUSION MATRIX
# ============================================================

confusion_path = os.path.join(
    MODEL_DIR,
    "confusion_matrix.csv"
)


np.savetxt(
    confusion_path,
    cm,
    delimiter=",",
    fmt="%d"
)


# ============================================================
# FINAL OUTPUT
# ============================================================

print()
print("=" * 60)
print("MODEL + NLP ARTIFACTS SAVED")
print("=" * 60)

print(
    f"Model       : {model_path}"
)

print(
    f"Vocabulary  : {words_path}"
)

print(
    f"Classes     : {classes_path}"
)

print(
    f"Evaluation  : {evaluation_path}"
)

print(
    f"Confusion   : {confusion_path}"
)

print("=" * 60)