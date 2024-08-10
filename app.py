import streamlit as st
import requests

# Function to interact with the chatbot API
def chat_with_bot(question, file=None):
    url = "http://localhost:5000/api/chat"  # Replace with your backend API URL
    files = {"file": file} if file else None
    data = {"question": question}

    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        return response.json().get("answer", "No response from the bot.")
    else:
        return "Failed to get a response from the bot."

# Streamlit app layout
st.title("E-commerce Recommender Chatbot")

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=["txt", "pdf"])

# Text input for the user question
user_input = st.text_input("Ask a question:")

# Button to send the query
if st.button("Send"):
    if user_input:
        # If a file is uploaded, send it along with the query
        file = uploaded_file.read() if uploaded_file else None
        response = chat_with_bot(user_input, file)
        st.text_area("Bot's response:", response, height=200)
    else:
        st.error("Please enter a question.")

# Optionally, you can display the uploaded file's content
if uploaded_file:
    file_details = {"filename": uploaded_file.name, "filetype": uploaded_file.type, "filesize": uploaded_file.size}
    st.write(file_details)

    if uploaded_file.type == "text/plain":
        st.text_area("File content", uploaded_file.getvalue().decode("utf-8"), height=200)
