import csv
import numpy as np
import re

from keras.models import load_model


# ============================================================
# PATHS
# ============================================================

MODEL_PATH = "models/chatbot_model.h5"
WORDS_PATH = "models/words.txt"
CLASSES_PATH = "models/classes.txt"
TEST_PATH = "data/challenge_test.csv"


# ============================================================
# LOAD MODEL
# ============================================================

model = load_model(
    MODEL_PATH
)


# ============================================================
# LOAD EXACT TRAINING VOCABULARY
# ============================================================

with open(
    WORDS_PATH,
    "r",
    encoding="utf-8"
) as file:

    words = [
        line.strip()
        for line in file
        if line.strip()
    ]


# ============================================================
# LOAD EXACT CLASS ORDER
# ============================================================

with open(
    CLASSES_PATH,
    "r",
    encoding="utf-8"
) as file:

    classes = [
        line.strip()
        for line in file
        if line.strip()
    ]


# ============================================================
# VERIFY MODEL
# ============================================================

print("=" * 70)
print("MODEL / VOCABULARY CHECK")
print("=" * 70)

print(
    f"Model input size : "
    f"{model.input_shape[-1]}"
)

print(
    f"Vocabulary size  : "
    f"{len(words)}"
)

print(
    f"Number of classes: "
    f"{len(classes)}"
)

print("=" * 70)


if model.input_shape[-1] != len(words):

    raise ValueError(
        "ERROR: Model input size and "
        "saved vocabulary size do not match."
    )


if model.output_shape[-1] != len(classes):

    raise ValueError(
        "ERROR: Model output classes and "
        "saved class list do not match."
    )


# ============================================================
# TOKENIZATION
# ============================================================

def tokenize(sentence):

    return re.findall(
        r"\b\w+\b",
        sentence.lower()
    )


# ============================================================
# BAG OF WORDS
# ============================================================

def bag_of_words(sentence):

    sentence_words = tokenize(
        sentence
    )

    bag = []

    for word in words:

        if word in sentence_words:

            bag.append(1)

        else:

            bag.append(0)

    return np.array(
        bag,
        dtype=np.float32
    )


# ============================================================
# PREDICTION
# ============================================================

def predict(sentence):

    bow = bag_of_words(
        sentence
    )

    prediction = model.predict(

        np.array([bow]),

        verbose=0
    )[0]

    index = np.argmax(
        prediction
    )

    return (
        classes[index],
        float(prediction[index])
    )


# ============================================================
# RUN CHALLENGE TEST
# ============================================================

total = 0
correct = 0

results = []


with open(
    TEST_PATH,
    newline="",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(
        file
    )

    for row in reader:

        text = row["text"].strip()

        expected = row[
            "expected_intent"
        ].strip()

        predicted, confidence = predict(
            text
        )

        total += 1

        if predicted == expected:

            correct += 1

        results.append(
            (
                text,
                expected,
                predicted,
                confidence
            )
        )


# ============================================================
# FINAL ACCURACY
# ============================================================

accuracy = (

    correct / total

    if total > 0

    else 0
)


print()
print("=" * 70)
print("UNSEEN CHALLENGE TEST")
print("=" * 70)

print(
    f"Total questions : "
    f"{total}"
)

print(
    f"Correct         : "
    f"{correct}"
)

print(
    f"Incorrect       : "
    f"{total - correct}"
)

print(
    f"Accuracy        : "
    f"{accuracy:.4f}"
)

print(
    f"Accuracy (%)    : "
    f"{accuracy * 100:.2f}%"
)

print("=" * 70)


# ============================================================
# INCORRECT PREDICTIONS
# ============================================================

incorrect = [

    result

    for result in results

    if result[1] != result[2]
]


print()
print(
    f"INCORRECT PREDICTIONS "
    f"({len(incorrect)})"
)

print("-" * 70)


if not incorrect:

    print(
        "No incorrect predictions."
    )

else:

    for (
        text,
        expected,
        predicted,
        confidence
    ) in incorrect:

        print()

        print(
            f"Question: "
            f"{text}"
        )

        print(
            f"Expected: "
            f"{expected}"
        )

        print(
            f"Predicted: "
            f"{predicted}"
        )

        print(
            f"Confidence: "
            f"{confidence:.4f}"
        )


print()
print("=" * 70)
print("CHALLENGE TEST COMPLETE")
print("=" * 70)