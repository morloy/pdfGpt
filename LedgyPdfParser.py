# Import required libraries
import streamlit as st
import PyPDF2
import requests
import openai
from io import BytesIO

default_prompt = """Return the data from the document as a JSON.

Use the following fields:
totalNumberOfShares
stakeholderName
grantDate
strikePrice
"""
default_model = "gpt-3.5-turbo"

# Set up the Streamlit app
st.title("LedGyPT PDF Parser")
st.write("Upload a PDF file, extract text and send it to GPT API with a custom prompt.")

# User interface components
openai_api_key = st.text_input("Enter your OpenAI API key (from 1Password)", placeholder="sk-…", type="password")
pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])

sample_document_name = "Option Grant Letter.pdf"
with open(sample_document_name, "rb") as file:
    btn = st.download_button(label="Download sample document", data=file, file_name=sample_document_name)
custom_prompt = st.text_area("Customize the prompt for GPT", default_prompt, height=200)
custom_model = st.selectbox("Select OpenAI model", ('gpt-3.5-turbo', 'gpt-4'))

submit_button = st.button("Submit")

# Function to read PDF and convert to text
def pdf_to_text(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Function to send the extracted text to GPT-4 API
def send_to_gpt4_api(text, prompt):
    openai.api_key = openai_api_key

    response = openai.ChatCompletion.create(
        model=custom_model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{prompt}\n{text}"}
        ],
        max_tokens=1000,
        temperature=0.5,
        top_p=1,
    )
    return response

# Process the PDF file and send the extracted text to GPT-4 API
if submit_button and openai_api_key and pdf_file and custom_prompt:
    with st.spinner("Extracting text from PDF..."):
        pdf_text = pdf_to_text(BytesIO(pdf_file.getvalue()))
        with st.expander("Extracted text from PDF"):
            st.code(pdf_text)

    with st.spinner("Sending text to GPT API..."):
        response = send_to_gpt4_api(pdf_text, custom_prompt)

    st.header("GPT API response:")
    print(response)
    st.json(response["choices"][0]["message"]["content"])
