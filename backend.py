from flask import Flask, request, jsonify
import os
import re
import PyPDF2
from io import BytesIO
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.llms import Cohere
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.vectorstores import Qdrant
from langchain.schema import Document
import tempfile

app = Flask(__name__)

# Cohere API key (set your key here)
COHERE_API_KEY = 'nTf1sAvJZ7u6fUgFpbpdpOcN8VnvIzOhiXksBpBj'  # Replace with your actual Cohere API key

# Function to read text files
def parse_txt(file):
    text = file.read().decode('utf-8')
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text

# Function to read and parse PDF files
def parse_pdf(file):
    pdf = PyPDF2.PdfReader(BytesIO(file.read()))
    output = []
    for page in pdf.pages:
        text = page.extract_text()
        text = re.sub(r"(\w+)-\n(\w+)", r"\1\2", text)
        text = re.sub(r"(?<!\n\s)\n(?!\s\n)", " ", text.strip())
        text = re.sub(r"\n\s*\n", "\n\n", text)
        output.append(text)
    return output

# Function to split text into smaller documents
def text_to_docs(text):
    if isinstance(text, str):
        text = [text]
    page_docs = [Document(page_content=page) for page in text]

    for i, doc in enumerate(page_docs):
        doc.metadata["page"] = i + 1

    doc_chunks = []
    for doc in page_docs:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=4000,
            separators=["\n\n", "\n", ".", "!", "?", ",", " "],
            chunk_overlap=0,
        )
        chunks = text_splitter.split_text(doc.page_content)
        for i, chunk in enumerate(chunks):
            doc_chunk = Document(
                page_content=chunk, metadata={"page": doc.metadata["page"], "chunk": i}
            )
            doc_chunk.metadata["source"] = f"{doc_chunk.metadata['page']}-{doc_chunk.metadata['chunk']}"
            doc_chunks.append(doc_chunk)
    return doc_chunks

# Main chatbot function
def chat_bot(question, file=None):
    if file:
        if file.filename.endswith(".txt"):
            doc = parse_txt(file)
        else:
            doc = parse_pdf(file)
        pages = text_to_docs(doc)
    else:
        return "No file provided."

    embeddings = CohereEmbeddings(
        model="multilingual-22-12", cohere_api_key=COHERE_API_KEY
    )
    store = Qdrant.from_documents(
        pages,
        embeddings,
        location=":memory:",
        collection_name="my_documents",
        distance_func="Dot",
    )

    prompt_template = """Text: {context}

    Question: {question}

    Answer the question based on the text provided. If the text doesn't contain the answer, reply that the answer is not available.
    You are an e-commerce recommender chatbot. Analyze the question and provide the top 5 products and their details like price, category, and description matching the user needs.
    If the user asks for cheap or economical products, sort by price.
    Only recommend the top 5 products for general recommendation and searching queries."""

    PROMPT = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"]
    )

    chain_type_kwargs = {"prompt": PROMPT}
    qa = RetrievalQA.from_chain_type(
        llm=Cohere(model="command", temperature=0, cohere_api_key=COHERE_API_KEY),
        chain_type="stuff",
        retriever=store.as_retriever(),
        chain_type_kwargs=chain_type_kwargs,
        return_source_documents=True,
    )

    answer = qa({"query": question})
    result = answer["result"].replace("\n", "").replace("Answer:", "")
    return result

# Flask route for handling the chatbot requests
@app.route('/api/chat', methods=['POST'])
def chat():
    question = request.form.get("question")
    file = request.files.get("file")
    response = chat_bot(question, file)
    return jsonify({"answer": response})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
