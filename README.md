# 🤖 E-commerce Customer Service Chatbot

An intelligent machine learning-based chatbot designed to handle common e-commerce customer queries such as order tracking, product inquiries, and returns.

---

## 🚀 Features

* Intent-based Natural Language Processing (NLP)
* Handles multiple variations of user queries
* Supports dynamic responses
* Trained on an augmented dataset for better accuracy
* Simple and interactive UI using Streamlit

---

## 🧠 Tech Stack

* Python
* TensorFlow / Keras
* NLTK
* NumPy
* Streamlit

---

## 📂 Project Structure

```
CHATBOT/
│
├── app.py                  # Streamlit frontend
├── train.py                # Model training script
├── models/
│   └── chatbot_model.h5    # Trained model
├── data/
│   └── augmented_intents.csv
├── src/
│   └── preprocess.py       # Data preprocessing
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```
git clone https://github.com/Pratham2105x/CHATBOT.git
cd CHATBOT
```

---

### 2. Install dependencies

```
pip install -r requirements.txt
```

---

### 3. Train the model

```
python train.py
```

---

### 4. Run the chatbot

```
streamlit run app.py
```

---

## 💬 Example Queries

* "Track my order"
* "Where is my order?"
* "Tell me about this product"
* "How do I return an item?"

---

## 📈 Improvements Made

* Expanded dataset with multiple query variations
* Improved intent recognition
* Better preprocessing and tokenization
* Enhanced response diversity

---

## 🔮 Future Improvements

* Add chat history (multi-turn conversations)
* Integrate with real e-commerce APIs
* Add Hinglish and typo handling
* Deploy as a web app (Flask/FastAPI)


