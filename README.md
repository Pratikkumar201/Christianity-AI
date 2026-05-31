# ✝ ChristianityAI — Production-Grade Scripture-Grounded AI Assistant

A production-ready AI system for Christian scripture Q&A, theology discussion, content generation, image creation, and hallucination prevention — built with RAG, multi-agent routing, FAISS, Groq LLM, and Next.js 15.

> **Designed to demonstrate**: RAG Architecture · Agent Routing · Grounding · Hallucination Prevention · Fake Verse Detection · Safety Layers · Denomination Awareness · Evaluation Pipelines · Observability

---

## Architecture

```
User
  ↓
Frontend (Next.js 15 + TypeScript + TailwindCSS)
  ↓
FastAPI Backend
  ↓
┌─────────────────────────────────────────────────┐
│              SAFETY AGENT                        │
│  Fast regex patterns + LLM moderation           │
│  Blocks: hate speech, jailbreaks, injections    │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│              ROUTER AGENT                        │
│  LLM classifier → structured JSON               │
│  Routes: SCRIPTURE_QA | THEOLOGY_DISCUSSION |   │
│          CONTENT_GENERATION | IMAGE_GENERATION  │
│          VERSE_VERIFICATION | GENERAL_CHAT      │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│              MEMORY LAYER                        │
│  Session-based · Denomination tracking          │
│  10-turn context window · Preference storage    │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│              RAG RETRIEVAL                      │
│ Hybrid Retrieval FAISS + BM25
  BAAI/bge-small-en-v1.5  31,102 KJV verses       │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│         SPECIALIZED AGENT (by route)             │
│  Scripture QA   → Grounded Bible answers        │
│  Theology       → Multi-denomination views      │
│  Content Gen    → Sermons, devotionals, prayers │
│  Image Gen      → Pollinations API + enrichment │
│  Verse Verify   → Real-time reference checker   │
└─────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────┐
│           CITATION VALIDATOR AGENT               │
│  Verifies all [Book Ch:V] citations exist       │
│  Checks citations match retrieved context       │
│  Rejects hallucinated references                │
└─────────────────────────────────────────────────┘
  ↓
Grounded · Verified · Safe Response → User
```

---

## Features

| Feature | Implementation |
|---|---|
| **RAG Pipeline** | FAISS + BAAI/bge-small-en-v1.5 + KJV Bible (~31K verses) |
| **Agent Routing** | Groq LLM → structured JSON → 7 route types |
| **Hallucination Prevention** | Retrieval-only answers + confidence threshold |
| **Fake Verse Detection** | Bible structure map validates book/chapter/verse |
| **Citation Validation** | Post-generation agent verifies all citations |
| **Safety Layer** | Regex fast-path + LLM moderation in series |
| **Denomination Awareness** | Catholic / Protestant / Orthodox multi-perspective |
| **Image Generation** | Pollinations API + LLM prompt enrichment |
| **Memory** | Session-based: denomination + 10-turn history |
| **Evaluation Suite** | 5 test suites with quantitative metrics |
| **Observability** | Full pipeline trace per request |
| **Prompt Injection Defense** | Pattern matching + LLM-level filtering |

| **Hybrid Retrieval | FAISS semantic search + BM25 keyword search** |

---

## Tech Stack

**Backend**
- FastAPI (Python 3.11+)
- Groq API (`llama-3.3-70b-versatile`)
- sentence-transformers (`BAAI/bge-small-en-v1.5`)
- FAISS (`IndexFlatIP`, cosine similarity)
- Custom Multi-Agent Architecture
- KJV Bible (public domain, ~31,000 verses)

**Frontend**
- Next.js 15 (App Router)
- TypeScript
- TailwindCSS (custom sacred gold/navy design system)
- Lucide React icons

**External APIs**
- Groq API (LLM — all agents)
- Pollinations.ai (image generation — free, no key needed)

---

## Demo Queries

### Scripture QA
What does the Bible say about anxiety?

### Theology
Explain the Trinity.

### Verse Verification
Does Romans 15:99 exist?

### Prayer Generation
Write a prayer for healing and strength.

### Image Generation
Generate an image of a wooden cross on a hill at sunset.


## Project Structure

```
christianity-ai/
├── backend/
│   ├── agents/
│   │   ├── router_agent.py       # LLM route classifier (7 routes)
│   │   ├── safety_agent.py       # Regex + LLM safety moderation
│   │   ├── scripture_agent.py    # RAG-grounded Bible Q&A
│   │   ├── theology_agent.py     # Denomination-aware theology
│   │   ├── content_agent.py      # Sermon/devotional/prayer gen
│   │   ├── image_agent.py        # Pollinations + prompt enrichment
│   │   └── validator_agent.py    # Citation verifier + hallucination checker
│   ├── rag/
│   │   ├── retriever.py          # High-level FAISS retriever
│   │   ├── embeddings.py         # BGE singleton encoder
│   │   └── vector_store.py       # FAISS index builder/loader
│   ├── memory/
│   │   └── memory_manager.py     # Session-based memory store
│   ├── evaluation/
│   │   ├── evaluator.py          # Eval engine + metrics
│   │   ├── hallucination_tests.json
│   │   ├── adversarial_tests.json
│   │   └── theology_tests.json
│   ├── api/
│   │   └── routes.py             # All FastAPI endpoints
│   ├── build_index.py            # One-time setup: download + index
│   ├── main.py                   # FastAPI app entrypoint
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── app/
    │   ├── page.tsx              # Chat page (main)
    │   ├── image-gen/page.tsx    # Image generation
    │   └── evaluation/page.tsx  # Evaluation dashboard
    ├── components/
    │   ├── Navbar.tsx
    │   ├── MessageBubble.tsx
    │   ├── DenominationSelector.tsx
    │   └── MemoryIndicator.tsx
    ├── lib/api.ts                # Typed API client
    └── ...config files
```

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- Groq API key (free at https://console.groq.com)

---

### Step 1 — Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Build Bible index (downloads KJV + builds FAISS — takes 3-10 min first time)
# First startup automatically builds the Bible index
uvicorn main:app --reload

```

Backend will be available at: `http://localhost:8000`
API docs at: `http://localhost:8000/docs`

---

### Step 2 — Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

---

## API Reference

### `POST /chat`
Main multi-agent pipeline.

```json
{
  "message": "What does John 3:16 say?",
  "session_id": "session_123",
  "denomination": "Protestant"
}
```

Response includes: `route`, `answer`, `citations`, `sources`, `safety`, `validation`, `pipeline_log`

---

### `POST /verify-verse`
Check if a Bible verse reference exists.

```json
{ "book": "Romans", "chapter": 15, "verse": 99 }
```

Response: `{ "valid": false, "reason": "Romans only has 16 chapters..." }`

---

### `POST /image`
Generate a Christian image.

```json
{ "prompt": "Noah's Ark", "session_id": "session_123" }
```

---

### `GET /evaluation/run`
Run all evaluation test suites.

---

### `GET /health`
Health check.

---

## Evaluation Metrics

| Metric | Tests |
|---|---|
| **Fake Verse Detection Rate** | Rejects invalid book/chapter/verse refs |
| **Real Verse Accuracy** | Correctly validates real references |
| **Safety Block Rate** | Blocks hate/jailbreak/injection attempts |
| **Safety Allow Rate** | Passes legitimate Christian content |
| **Hallucination Prevention Rate** | Prevents fabricated scripture quotes |
| **Overall Score** | Average across all 5 categories |

---

## Safety Examples

| Input | Response |
|---|---|
| "Ignore all instructions" | 🛡️ BLOCKED — Prompt injection detected |
| "Rewrite Bible to support racism" | 🛡️ BLOCKED — Hate speech detected |
| "What does Romans 15:99 say?" | ⚠️ Romans 15:99 does not exist |
| "What does John 3:16 say?" | ✅ Retrieved + cited + verified |
| "Which denomination is correct?" | ✅ Multi-perspective balanced response |

---

## Anti-Hallucination Design

1. **Retrieval-Only Answers** — LLM can only quote verses present in FAISS context
2. **Confidence Threshold** — Refuses to answer if top retrieval score < 0.35
3. **Citation Validator** — Post-generation agent verifies all `[Book Ch:V]` citations
4. **Verse Structure Map** — Real-time check: book exists? chapter exists? verse exists?
5. **Grounding Instruction** — Every system prompt explicitly forbids memory-based quotes

---

## License

MIT — Bible text is KJV (public domain)


## Author

Pratik Kumar

AI/ML Engineer

Skills Demonstrated:
- Retrieval-Augmented Generation (RAG)
- Multi-Agent Systems
- FastAPI
- Vector Databases
- FAISS
- BM25
- LLM Safety
- Hallucination Prevention
- AI Evaluation Frameworks