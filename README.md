# Semantic Search Engine

A full-stack semantic search application using dense vector retrieval with Sentence-BERT embeddings and FAISS indexing, compared side-by-side with BM25 keyword search.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [API Endpoints](#api-endpoints)
- [Frontend](#frontend)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

This semantic search engine demonstrates how dense retrieval (embedding-based search) compares to traditional keyword search (BM25). Built with **FastAPI** backend and **React + Vite** frontend, it indexes ~50,000 Wikipedia vectors and provides real-time semantic search with performance metrics.

**Key Capabilities:**
- Dense semantic search using Sentence-BERT embeddings
- BM25 keyword-based baseline search
- Side-by-side comparison of both methods
- Latency metrics (p50, p95, p99)
- Query result caching with LRU cache

---

## ✨ Features

### Core Search Features
- **Semantic Search**: Dense vector retrieval using SBERT embeddings + FAISS
- **BM25 Search**: Traditional keyword-based search baseline
- **Compare Mode**: View semantic vs. BM25 results side-by-side
- **Performance Metrics**: Real-time latency tracking (p50, p95, p99)
- **Query Caching**: LRU cache (512 entries) for frequently searched queries
- **Health Check**: `/health` endpoint to verify indexing status

### Frontend Features
- **Dark-themed UI**: Modern Tailwind CSS interface
- **Real-time Search**: Responsive search with Enter key support
- **Result Display**: Shows title, snippet, Wikipedia URL, score, and document ID
- **Loading State**: Visual feedback during search
- **Stats Display**: Shows latency, total hits, and search method used

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn 0.30.6
- **Embeddings**: Sentence-Transformers 3.1.1 (all-MiniLM-L6-v2)
- **Vector Search**: FAISS (faiss-cpu 1.8.0)
- **Keyword Search**: rank-bm25 0.2.2
- **NLP Processing**: NLTK 3.9.1
- **Data Validation**: Pydantic 2.9.2
- **Configuration**: python-dotenv 1.0.1, pydantic-settings 2.5.2
- **LLM Integration**: Groq
- **Utilities**: NumPy 1.26.4, Datasets 3.0.1

### Frontend
- **Framework**: React 19.2.4
- **Build Tool**: Vite 8.0.1
- **Styling**: Tailwind CSS 4.2.2 + PostCSS
- **Linting**: ESLint 9.39.4
- **Type Support**: React types 19.2.14

### Infrastructure
- **Containerization**: Docker (Dockerfile included)
- **Version Control**: Git
- **Environment Management**: .env files

---

## 📁 Project Structure

```
semantic-search-engine/
├── backend/                          # FastAPI backend service
│   ├── main.py                       # FastAPI app with /search, /search/bm25, /search/compare endpoints
│   ├── indexer.py                    # SemanticIndex class (SBERT + FAISS)
│   ├── bm25_index.py                 # BM25Index class for keyword search
│   ├── models.py                     # Pydantic models (SearchResult, SearchResponse, CompareResponse, MetricsResponse)
│   ├── config.py                     # Configuration (paths, model name, cache size)
│   ├── build_index.py                # Script to build FAISS + BM25 indexes from documents
│   ├── requirements.txt               # Python dependencies
│   ├── pyproject.toml                # Python project config
│   ├── Dockerfile                    # Docker image for backend
│   ├── .python-version               # Python version specification
│   ├── data/                         # Index data directory
│   │   ├── faiss.index              # FAISS binary index
│   │   ├── metadata.json            # Document metadata (title, text, url, doc_id)
│   │   └── bm25.pkl                 # Pickled BM25 index
│   └── uv.lock                       # Dependency lock file
│
├── frontend/                         # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx                  # Main search component with UI
│   │   ├── main.jsx                 # React entry point
│   │   ├── App.css                  # Component styles
│   │   ├── index.css                # Global styles
│   │   └── assets/                  # Static assets
│   ├── public/                      # Public assets
│   ├── index.html                   # HTML template
│   ├── package.json                 # NPM dependencies
│   ├── vite.config.js               # Vite build configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   ├── postcss.config.js            # PostCSS config
│   ├── eslint.config.js             # ESLint rules
│   └── Dockerfile                   # Docker image for frontend
│
├── .gitignore                        # Git ignore rules
└── docker-compose.yml (if exists)   # Docker Compose orchestration
```

---

## 📋 Prerequisites

- **Python** 3.8+
- **Node.js** 16+
- **Docker** (optional, for containerization)

---

## 🚀 Installation & Setup

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create Python virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Build indexes (first time only):**
```bash
python build_index.py
```
This generates:
- `data/faiss.index` (FAISS vector index)
- `data/metadata.json` (document metadata)
- `data/bm25.pkl` (BM25 index)

5. **Start FastAPI server:**
```bash
python main.py
```
Or with uvicorn:
```bash
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

Server runs at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Start development server:**
```bash
npm run dev
```

Frontend runs at `http://localhost:5173`

### Using Docker

```bash
# Build and run both services
docker-compose up --build

# Or individually
docker build -t semantic-backend ./backend
docker build -t semantic-frontend ./frontend

docker run -p 8000:8000 semantic-backend
docker run -p 5173:5173 semantic-frontend
```

---

## 🔌 API Endpoints

All endpoints return JSON responses. Base URL: `http://127.0.0.1:8000`

### 1. Semantic Search
**GET** `/search?q=<query>&k=<num_results>`

**Query Parameters:**
- `q` (required): Search query string (1-500 characters)
- `k` (optional): Number of results to return (1-50, default: 10)

**Response:**
```json
{
  "query": "cardiac arrest",
  "results": [
    {
      "doc_id": "doc_123",
      "title": "Cardiac arrest",
      "snippet": "Cardiac arrest is when the heart stops beating...",
      "url": "https://en.wikipedia.org/wiki/Cardiac_arrest",
      "score": 0.8934
    }
  ],
  "latency_ms": 45.32,
  "total_hits": 10,
  "method": "semantic"
}
```

### 2. BM25 Keyword Search
**GET** `/search/bm25?q=<query>&k=<num_results>`

**Query Parameters:**
- `q` (required): Search query
- `k` (optional): Number of results (1-50, default: 10)

**Response:** Same format as semantic search but with `"method": "bm25"`

### 3. Compare Search (Side-by-side)
**GET** `/search/compare?q=<query>&k=<num_results>`

**Query Parameters:**
- `q` (required): Search query
- `k` (optional): Number of results per method (1-20, default: 5)

**Response:**
```json
{
  "query": "cardiac arrest",
  "semantic": [
    { "doc_id": "...", "title": "...", ... }
  ],
  "bm25": [
    { "doc_id": "...", "title": "...", ... }
  ],
  "latency_ms": 78.45
}
```

### 4. Health Check
**GET** `/health`

**Response:**
```json
{
  "status": "ok",
  "docs_indexed": 50000
}
```

### 5. Metrics
**GET** `/metrics`

Returns latency percentiles over the last 10,000 requests:
```json
{
  "p50": 35.2,
  "p95": 125.8,
  "p99": 280.1,
  "total_requests": 10000
}
```

---

## 🎨 Frontend

### App Component (App.jsx)

The main React component handles:
- **Search Input**: Text input with Enter key support
- **Search Button**: Triggers API call to backend
- **Results Display**: Maps through results array, displays title, snippet, score, URL, and doc_id
- **Loading State**: Shows spinner during search
- **Stats Bar**: Displays latency (ms), total hits, and search method

### Key Features
- Fetches from `http://127.0.0.1:8000/search` endpoint
- Processes JSON response and extracts results array
- Error handling with user-friendly alert
- Tailwind CSS dark theme with hover effects
- Console logging for debugging (search logs at steps 1-4)

---

## 🔍 How It Works

### Semantic Search Flow

1. **Query Encoding**: User query → embedded to 384-dim vector using Sentence-BERT (all-MiniLM-L6-v2)
2. **Vector Search**: FAISS inner-product search (= cosine similarity since vectors are normalized)
3. **Result Mapping**: Top-k indices → fetch metadata from JSON
4. **Response**: Return SearchResult objects with scores

### BM25 Search Flow

1. **Tokenization**: Query → BM25 tokenizer
2. **Ranking**: rank-bm25 algorithm computes relevance scores
3. **Response**: Return SearchResult objects with BM25 scores

### Caching

- LRU cache (512 entries) on `_cached_semantic_search()` function
- Avoids re-embedding identical queries
- Cache key: `(query_lowercase, k)`

### Performance

- **Typical latency**: 30–80ms on CPU for 100k-doc corpus
- **Encoding speed**: ~2,000 docs/sec (CPU with MiniLM)
- **Memory**: FAISS IndexFlatIP (suitable up to ~1M vectors)

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add your feature'`)
6. Push and open a Pull Request

---

## 📄 License

This project is open source. Check LICENSE file for details.

---

## 🎓 Key Technologies Explained

### Sentence-BERT (SBERT)
Pre-trained transformer model that generates semantic embeddings. The `all-MiniLM-L6-v2` variant:
- Dimension: 384
- Speed: Fast (suitable for real-time use)
- Quality: Strong for semantic similarity tasks

### FAISS
Meta's open-source library for efficient similarity search and clustering of dense vectors.
- **IndexFlatIP**: Exhaustive search with inner-product distance (used here)
- O(n) query time but guaranteed exact results

### BM25
Probabilistic ranking function used in information retrieval. Balances:
- Term frequency (TF)
- Inverse document frequency (IDF)
- Document length normalization

---

## 📚 File Reference

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application, endpoints, request handling |
| `indexer.py` | SemanticIndex class for SBERT + FAISS operations |
| `bm25_index.py` | BM25Index class for keyword search |
| `models.py` | Pydantic data models for request/response validation |
| `config.py` | Configuration settings (paths, model names, cache size) |
| `build_index.py` | Index building script (one-time setup) |
| `App.jsx` | Main React component with UI and API integration |
| `App.css` | Component-specific styles |

---

**Created**: April 1, 2026 07:02:25 UTC  
**Author**: [@kundankumar-35](https://github.com/kundankumar-35)