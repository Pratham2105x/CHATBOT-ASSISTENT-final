import csv
import random
import numpy as np
from keras.models import load_model
import nltk
from nltk.stem import WordNetLemmatizer
from preprocess import words, classes, lemmatizer

# Load the trained model
try:
    model = load_model('models/chatbot_model.h5')
except Exception as e:
    print(f"Error loading model: {e}")
    exit()

# Load the intents file
intents = []
try:
    with open('data/intents.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            intents.append({
                'tag': row['tag'],
                'patterns': row['patterns'].split('|'),
                'responses': row['responses'].split('|')
            })
except FileNotFoundError:
    print("Intents file not found. Please ensure 'data/intents.csv' exists.")
    exit()
except Exception as e:
    print(f"Error reading intents file: {e}")
    exit()

import re

def clean_up_sentence(sentence):
    sentence_words = re.findall(r'\b\w+\b', sentence.lower())
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    return sentence_words


def bag_of_words(sentence, words):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence, model):
    bow = bag_of_words(sentence, words)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list

def get_response(ints, intents):
    if ints:
        tag = ints[0]['intent']
        for intent in intents:
            if intent['tag'] == tag:
                return random.choice(intent['responses'])
    return "Sorry, I do not understand that."

print("Chatbot is running! (type 'quit' to stop)")
while True:
    try:
        message = input("> ")
        if message.lower() == "quit":
            break
        ints = predict_class(message, model)
        res = get_response(ints, intents)
        print(res)
    except KeyboardInterrupt:
        print("\nExiting chatbot. Goodbye!")
        break
    except Exception as e:
        print(f"An error occurred: {e}")
