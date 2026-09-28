import nltk
from nltk.corpus import wordnet


# ============================================================
# DOWNLOAD WORDNET IF REQUIRED
# ============================================================

try:
    nltk.data.find("corpora/wordnet")
except LookupError:
    nltk.download("wordnet", quiet=True)


# ============================================================
# E-COMMERCE VOCABULARY
# ============================================================

DOMAIN_SYNONYMS = {

    "cost": ["price"],
    "costing": ["price"],
    "rate": ["price"],
    "rates": ["price"],
    "charge": ["price"],

    "parcel": ["package"],
    "shipment": ["shipping"],
    "ship": ["shipping"],
    "shipped": ["shipping"],

    "track": ["tracking"],
    "tracked": ["tracking"],
    "follow": ["tracking"],

    "purchase": ["order"],
    "purchased": ["order"],
    "buy": ["order"],
    "bought": ["order"],

    "item": ["product"],
    "goods": ["product"],

    "pay": ["payment"],
    "paid": ["payment"],

    "reimbursement": ["refund"],
    "reimburse": ["refund"],

    "signin": ["login"],

    "spec": ["specification"],
    "specs": ["specification"],

    "info": ["information"],
    "details": ["information"],
}


# ============================================================
# GET DOMAIN SYNONYMS
# ============================================================

def get_domain_synonyms(word, vocabulary):

    result = set()

    for synonym in DOMAIN_SYNONYMS.get(word, []):

        if synonym in vocabulary:
            result.add(synonym)

    return result


# ============================================================
# GET WORDNET SYNONYMS
# ============================================================

def get_wordnet_synonyms(word, vocabulary):

    result = set()

    try:
        synsets = wordnet.synsets(word)
    except Exception:
        return result

    for synset in synsets:

        for lemma in synset.lemmas():

            synonym = lemma.name().lower()

            synonym = synonym.replace(
                "_",
                " "
            )

            # Only use words already known
            # by our ML vocabulary.
            if (
                " " not in synonym
                and synonym in vocabulary
            ):
                result.add(synonym)

    return result


# ============================================================
# EXPAND TOKENS
# ============================================================

def expand_tokens(tokens, vocabulary):

    vocabulary = set(vocabulary)

    expanded = list(tokens)

    for token in tokens:

        # Our e-commerce dictionary
        expanded.extend(
            get_domain_synonyms(
                token,
                vocabulary
            )
        )

        # WordNet
        expanded.extend(
            get_wordnet_synonyms(
                token,
                vocabulary
            )
        )

    # Remove duplicates
    return list(
        dict.fromkeys(expanded)
    )