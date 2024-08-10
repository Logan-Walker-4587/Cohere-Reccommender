import streamlit as st
from flask import Flask, request, jsonify
from threading import Thread
import requests
from werkzeug.serving import run_simple

# Initialize Flask app
app = Flask(__name__)

@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.form.get('question')
    # Process the question with your model
    response = {"answer": f"Processed: {question}"}
    return jsonify(response)

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
