# Nimbus Cloud AI Chatbot

A simple, beginner-friendly AI Chatbot web application for **Nimbus Cloud** (a cloud storage service for small businesses). Built with **Python**, **FastAPI**, **Anthropic API (Claude)**, and a **Vanilla HTML/CSS/JS** frontend.

---

## 📁 Project Structure

```text
/
├── main.py           # FastAPI backend application
├── requirements.txt  # Python package dependencies
├── .env.example      # Template for environment configuration
├── README.md         # Setup and usage instructions
└── static/
    └── index.html    # Frontend user interface (HTML/CSS/JS)
```

---

## 🚀 Step-by-Step Setup Guide

### 1. Install Dependencies

First, ensure Python 3.8 or later is installed. Install all required packages using `pip`:

```bash
pip install -r requirements.txt
```

> **Included Packages:**
> - `fastapi`: Web framework for building APIs.
> - `uvicorn`: ASGI server to run FastAPI.
> - `anthropic`: Official Python client SDK for Anthropic Claude models.
> - `python-dotenv`: Loads environment variables from `.env`.
> - `pydantic`: Data validation and settings management.

---

### 2. Configure Your Anthropic API Key

Create a `.env` file in the project root directory by copying `.env.example`:

**Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**
```bash
cp .env.example .env
```

Open `.env` and replace `your-api-key-here` with your actual Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxx
```

---

### 3. Start the FastAPI Backend Server

Run the Uvicorn development server:

```bash
uvicorn main:app --reload
```

The server will start at `http://127.0.0.1:8000`.

---

### 4. Open the Chatbot in Your Browser

Open your web browser and navigate to:

👉 **[http://127.0.0.1:8000](http://127.0.0.1:8000)**

You will see the Nimbus Cloud support chatbot interface. Try asking questions like:
- *"What plans do you offer?"*
- *"How much is Nimbus Team?"*
- *"Do you offer a free trial?"*
- *"What platforms are supported?"*
- *"Can I store physical hardware?"* *(The bot will answer that it doesn't know based on its system prompt instructions!)*

---

## 💡 How It Works

1. **Frontend (`static/index.html`)**: Captures user input and sends a JSON payload to `POST /chat` using JavaScript `fetch()`.
2. **Backend (`main.py`)**:
   - Reads the incoming message using Pydantic schema validation.
   - Loads `ANTHROPIC_API_KEY` securely from `.env`.
   - Sends the message along with a strict Nimbus Cloud system prompt to the Anthropic API (`claude-sonnet-5`).
   - Returns Claude's response back to the frontend.
