import os
import json
import re

import numpy as np

from keras.models import load_model
from nltk.stem import WordNetLemmatizer

from src.lexicon import expand_tokens
from src.rules import rule_based_intent


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = load_model(
    os.path.join(
        MODEL_DIR,
        "chatbot_model.h5"
    )
)


# ============================================================
# LOAD VOCABULARY
# ============================================================

with open(
    os.path.join(
        MODEL_DIR,
        "words.json"
    ),
    "r",
    encoding="utf-8"
) as file:

    words = json.load(file)


# ============================================================
# LOAD INTENT CLASSES
# ============================================================

with open(
    os.path.join(
        MODEL_DIR,
        "classes.json"
    ),
    "r",
    encoding="utf-8"
) as file:

    classes = json.load(file)


# ============================================================
# NLP
# ============================================================

lemmatizer = WordNetLemmatizer()


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"[^\w\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# TOKENIZE
# ============================================================

def tokenize(text):

    normalized = normalize_text(
        text
    )

    tokens = normalized.split()

    return [
        lemmatizer.lemmatize(
            word
        )
        for word in tokens
    ]


# ============================================================
# BAG OF WORDS
# ============================================================

def bag_of_words(text):

    tokens = tokenize(
        text
    )

    # Add controlled dictionary synonyms
    expanded_tokens = expand_tokens(
        tokens,
        words
    )

    vocabulary = {
        word: index
        for index, word in enumerate(words)
    }

    bag = np.zeros(
        len(words),
        dtype=np.float32
    )

    for token in expanded_tokens:

        if token in vocabulary:

            bag[
                vocabulary[token]
            ] = 1.0

    return bag, tokens, expanded_tokens


# ============================================================
# INTENT PREDICTION
# ============================================================

def predict_intent(text):

    # --------------------------------------------------------
    # PREPROCESSING
    # --------------------------------------------------------

    normalized_text = normalize_text(
        text
    )

    tokens = tokenize(
        text
    )


    # --------------------------------------------------------
    # RULE-BASED CLASSIFICATION
    # --------------------------------------------------------

    rule_result = rule_based_intent(
        text
    )


    if rule_result is not None:

        return {
            "intent": rule_result["intent"],
            "confidence": 1.0,
            "method": "rule",

            # These fields are kept because
            # the existing app.py expects them.
            "normalized_text": normalized_text,
            "tokens": tokens,
            "expanded_tokens": tokens,
            "original_text": text,
        }


    # --------------------------------------------------------
    # ML CLASSIFICATION
    # --------------------------------------------------------

    bow, tokens, expanded_tokens = (
        bag_of_words(text)
    )


    # --------------------------------------------------------
    # SAFETY CHECK
    # --------------------------------------------------------

    if len(bow) != model.input_shape[-1]:

        raise RuntimeError(
            "Model and vocabulary do not match.\n"
            f"Model expects: {model.input_shape[-1]}\n"
            f"Vocabulary has: {len(bow)}\n\n"
            "Run: python train.py"
        )


    # --------------------------------------------------------
    # PREDICTION
    # --------------------------------------------------------

    prediction = model.predict(
        np.array(
            [bow]
        ),
        verbose=0
    )[0]


    predicted_index = int(
        np.argmax(
            prediction
        )
    )


    confidence = float(
        prediction[
            predicted_index
        ]
    )


    intent = classes[
        predicted_index
    ]


    # --------------------------------------------------------
    # RETURN FULL COMPATIBLE RESULT
    # --------------------------------------------------------

    return {

        "intent": intent,

        "confidence": confidence,

        "method": "ml",

        "normalized_text": normalized_text,

        "tokens": tokens,

        "expanded_tokens": expanded_tokens,

        "original_text": text,
    }


# ============================================================
# SIMPLE TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("SHOPBOT NLU TEST")
    print("=" * 60)

    print(
        "Model input size :",
        model.input_shape[-1]
    )

    print(
        "Vocabulary size  :",
        len(words)
    )

    print(
        "Number of intents:",
        len(classes)
    )

    print("=" * 60)


    questions = [

        "any discounts available?",

        "is there a sale?",

        "what is the cost?",

        "how much is this?",

        "is this in stock?",

        "what are the specs?",

        "what is the warranty?",

        "where is my parcel?",

        "when will my package arrive?",

        "i want to return this",

        "how long does a refund take?",

        "can i cancel my order?",

        "where are my old orders?",

        "what payment options do you have?",
    ]


    for question in questions:

        result = predict_intent(
            question
        )

        print()
        print(
            "Question   :",
            question
        )

        print(
            "Intent     :",
            result["intent"]
        )

        print(
            "Confidence :",
            round(
                result["confidence"],
                4
            )
        )

        print(
            "Method     :",
            result["method"]
        )

        print(
            "Normalized :",
            result["normalized_text"]
        )

        print("-" * 60)