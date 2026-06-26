# 📄 DocMind AI

An AI-powered Document Assistant built with **Python**, **Streamlit**, and **Hugging Face** that allows users to upload PDF documents, generate summaries, and ask natural language questions based on the document content.

---

## 🚀 Live Demo

docmind-ai-wxbmltzvsrvopqxaxwzqkw.streamlit.app

---

## ✨ Features

- 📄 Upload PDF documents
- 🤖 AI-powered document summarization
- 💬 Ask questions about uploaded documents
- 🔍 Semantic search using document chunking
- 📚 Conversation history
- 🌙 Modern dark UI
- ⚡ Powered by Hugging Face Inference API

---

## 🛠️ Tech Stack

- Python 3.12+
- Streamlit
- Hugging Face Hub
- PyMuPDF (fitz)
- Sentence Transformers
- Scikit-learn
- NumPy
- Pandas

---

## 📂 Project Structure

```
DocMind-AI/
│
├── app.py
├── requirements.txt
├── README.md
│
├── utils/
│   ├── llm_client.py
│   ├── pdf_processor.py
│   ├── session.py
│
├── .streamlit/
│   └── config.toml
│
└── assets/
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/docmind-ai.git
```

### 2. Go to the project folder

```bash
cd docmind-ai
```

### 3. Create a virtual environment

Windows

```bash
python -m venv venv
```

Activate it

```bash
venv\Scripts\activate
```

Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 5. Create a Hugging Face Token

Go to

https://huggingface.co/settings/tokens

Create a new Access Token.

---

### 6. Run the application

```bash
python -m streamlit run app.py
```

The application will start at

```
http://localhost:8501
```

---

## 📋 How to Use

1. Launch the application.
2. Paste your Hugging Face API Token.
3. Select an AI model.
4. Upload a PDF document.
5. Click **Summarize this document** or ask questions in the chat.
6. Receive AI-generated responses based on the uploaded document.

---

## 📦 Requirements

Example `requirements.txt`

```text
streamlit
huggingface_hub
PyMuPDF
sentence-transformers
numpy
pandas
scikit-learn
torch
transformers
```

---

## 📸 Screenshots

### Home

<img width="1905" height="903" alt="image" src="https://github.com/user-attachments/assets/696ce76a-b63c-4ce5-b7a6-e1c3ced686da" />


### Document Upload

<img width="1901" height="897" alt="image" src="https://github.com/user-attachments/assets/1c52ab7f-c74a-44ca-8fbf-e4fcd533d559" />


### AI Chat

<img width="1898" height="913" alt="image" src="https://github.com/user-attachments/assets/b47a8b15-8fca-44d4-8e45-24d9a71795b2" />
<img width="1901" height="892" alt="image" src="https://github.com/user-attachments/assets/0ef08143-967d-4c06-9cee-204c7c2cfa40" />
<img width="1452" height="930" alt="image" src="https://github.com/user-attachments/assets/6b2afef5-a48a-4874-873f-b5d01ec4efd3" />


---

## 🚀 Future Improvements

- Multiple PDF support
- Export chat to PDF
- Export chat to TXT
- Source page citations
- OCR support for scanned PDFs
- Authentication
- Voice interaction
- Multi-language support

---

## 👩‍💻 Author

**Pratishtha Verma**

GitHub: https://github.com/pratishthaverma67

LinkedIn: www.linkedin.com/in/pratishtha-verma-39414a368

---


## ⭐ If you found this project useful

Please consider giving the repository a ⭐ on GitHub.
