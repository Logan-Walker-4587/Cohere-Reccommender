import streamlit as st
from flask import Flask, request, jsonify
from threading import Thread
import cohere
import requests
from werkzeug.serving import run_simple

# Initialize Flask app
app = Flask(__name__)

# Initialize Cohere API
cohere_client = cohere.Client('nTf1sAvJZ7u6fUgFpbpdpOcN8VnvIzOhiXksBpBj')  # Replace with your actual API key

@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.form.get('question')
    # Use your Cohere model to process the question
    response = cohere_client.generate(
        model='large',
        prompt=question,
        max_tokens=50,
    )
    return jsonify({"answer": response.generations[0].text.strip()})

# Function to run Flask in a thread
def run_flask():
    run_simple('0.0.0.0', 5000, app)

# Start the Flask app in a separate thread
Thread(target=run_flask).start()

# Streamlit frontend code
st.title("E-commerce Recommender Chatbot")

user_input = st.text_input("Ask a question:")
if st.button("Send"):
    if user_input:
        # Make a request to the local Flask API
        response = requests.post("http://localhost:5000/api/chat", data={"question": user_input})
        st.text_area("Bot's response:", response.json().get("answer", "No response from the bot."))
    else:
        st.error("Please enter a question.")
