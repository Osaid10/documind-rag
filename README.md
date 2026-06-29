# DocuMind — Intelligent Document Q&A System

> Upload any document. Ask any question. Get answers with exact source citations.

DocuMind is a fully local, privacy-first RAG (Retrieval-Augmented Generation) application that lets you have a conversation with your PDF, Word, and text documents. Every answer is grounded in your actual documents — with page numbers and highlighted passages as evidence.

---

## Screenshots / Demo

> **See the full demo video:** [link to Fiverr gig / YouTube]

| Upload & Index | Q&A with Citations |
|---|---|
| *Drag-and-drop your documents; watch real-time indexing stats* | *Ask questions, get answers with source passages highlighted* |

---

## Features

- **Multi-format support** — PDF, DOCX, and plain text files
- **100% local & private** — No data leaves your machine; no paid APIs required
- **Source citations** — Every AI answer links to the exact passage and page number it came from
- **Persistent storage** — Documents stay indexed between sessions via ChromaDB on disk
- **Multi-document Q&A** — Upload several documents and query across all of them simultaneously
- **Document management** — Delete individual documents from the index without affecting others
- **Polished UI** — Dark glassmorphism design with animated thinking indicator

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.11+ | [python.org](https://www.python.org/downloads/) |
| Ollama | latest | [ollama.ai](https://ollama.ai) |
| RAM | 8 GB+ | 16 GB recommended for mistral:7b |
| GPU (optional) | — | Tested on RTX 3050 6 GB; CPU-only works but is slower |

**Pull the default model before running:**

```bash
ollama pull mistral
```

> Tested on RTX 3050 6 GB / 16 GB RAM with `mistral:7b`. Inference takes ~5–15 s per query on this hardware.

---

## Quick Start

### Option A — Local (PowerShell, Windows)

```powershell
# Clone the repo
git clone https://github.com/your-username/documind.git
cd documind

# Start Ollama in a separate terminal
ollama serve

# Run DocuMind (creates venv, installs deps, launches browser)
.\run.ps1

# Optional: use a different model
.\run.ps1 -Model llama3
```

### Option B — Docker Compose

```bash
# Make sure Ollama is running on the host first
ollama serve

# Build and start DocuMind
docker compose up --build

# Open http://localhost:8501
```

> On Linux/Mac, Docker's `host-gateway` extra_host mapping lets the container reach Ollama on `localhost:11434`.

### Option C — Manual (Linux / macOS)

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

export OLLAMA_MODEL=mistral   # or llama3, gemma2, etc.
streamlit run app/main.py
```

---

## How It Works

```
User uploads PDF/DOCX/TXT
         │
         ▼
  Text extraction (PyMuPDF / python-docx)
         │
         ▼
  Chunking (2 000-char chunks, 200-char overlap, sentence-boundary-aware)
         │
         ▼
  Embedding (sentence-transformers all-MiniLM-L6-v2, runs locally)
         │
         ▼
  Vector storage (ChromaDB, persisted to app/storage/chroma_db/)
         │
  User asks a question
         │
         ▼
  Query embedded → cosine similarity search → top-4 chunks retrieved
         │
         ▼
  Prompt built: context chunks + question injected into template
         │
         ▼
  Ollama LLM generates answer (mistral:7b by default)
         │
         ▼
  Answer + source citations displayed in UI
```

---

## Tech Stack

| Layer | Technology | Why |
|---|---|---|
| UI framework | [Streamlit](https://streamlit.io) | Rapid, Python-native web UI |
| LLM | [Ollama](https://ollama.ai) + Mistral 7B | Fully local, no API key needed |
| Embeddings | [sentence-transformers](https://www.sbert.net) `all-MiniLM-L6-v2` | Fast, high-quality, free |
| Vector DB | [ChromaDB](https://www.trychroma.com) | Embedded, persistent, no server required |
| PDF parsing | [PyMuPDF](https://pymupdf.readthedocs.io) (`fitz`) | Fast and accurate text + page extraction |
| DOCX parsing | [python-docx](https://python-docx.readthedocs.io) | Standard Word document library |
| Container | Docker + Docker Compose | One-command deployment |

---

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `mistral` | Model name to use for chat |

You can set these in a `.env` file or pass them directly:

```bash
OLLAMA_MODEL=llama3 streamlit run app/main.py
```

---

## Project Structure

```
documind/
├── app/
│   ├── main.py          # Streamlit entry point — app logic & layout
│   ├── rag.py           # RAG pipeline: parse, chunk, embed, retrieve
│   ├── llm.py           # Ollama API client wrapper
│   └── ui.py            # CSS design system & HTML component helpers
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── run.ps1              # One-click Windows launcher
└── README.md
```

---

## Changing the LLM Model

DocuMind works with any model available in Ollama:

```bash
ollama pull llama3        # Meta Llama 3 8B
ollama pull gemma2        # Google Gemma 2 9B
ollama pull phi3          # Microsoft Phi-3 Mini (lightweight)
ollama pull qwen2         # Alibaba Qwen 2 7B
```

Then launch with:

```powershell
.\run.ps1 -Model llama3
```

---

## License

MIT — free to use, modify, and distribute.

---

*Built as a portfolio project demonstrating production-quality RAG system design with fully local AI infrastructure.*
