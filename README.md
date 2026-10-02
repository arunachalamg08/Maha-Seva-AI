# MahaSeva AI Pro (महासेवा AI Pro)

## One Intelligent Digital Gateway for Maharashtra Government Services

> ⚠ **Technology Prototype** — This is a demonstration platform. It is NOT an official Government of Maharashtra website and is not affiliated with or endorsed by any government department.

---

## 🏛️ What is MahaSeva AI Pro?

MahaSeva AI Pro is a full-stack citizen-service intelligence platform that demonstrates how AI, real-time APIs, multilingual interfaces, document intelligence, and grievance management can work together to serve Maharashtra's citizens.

### Core Capabilities

| Module | Description |
|--------|-------------|
| **Scheme Explorer** | Browse 12+ Maharashtra government schemes with eligibility, documents, GR references |
| **Service Guide** | Step-by-step guide to 8+ RTS Act services with timelines and fees |
| **Smart Eligibility Checker** | Multi-step form evaluating citizen eligibility across all schemes |
| **AI Assistant** | Gemini-powered multilingual Q&A (Marathi, Hindi, English) with zero-hallucination RAG |
| **Grievance Portal (Nivaran)** | File, track, and manage citizen grievances with priority scoring |
| **Document Intelligence** | AI-assisted document analysis and requirement checking |
| **District Directory** | Setu Kendras, department helplines, collectorate info |
| **Admin Dashboard** | Grievance analytics, system health, audit logs |

### Three User Roles

- **Citizen** — Discover services, check eligibility, ask questions, file grievances
- **Officer** — Manage grievances, update statuses, department dashboards
- **Administrator** — System health, API management, knowledge management, audit logs

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (SPA)                        │
│           Vanilla HTML/CSS/JS • Responsive               │
│         Multilingual (EN / मराठी / हिंदी)                │
└──────────────────────┬───────────────────────────────────┘
                       │ REST API
┌──────────────────────▼───────────────────────────────────┐
│                  FastAPI Backend                         │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │ AI Provider  │  │ Core Engines │  │ Auth (JWT)     │  │
│  │ Abstraction  │  │              │  │                │  │
│  │  ┌─Gemini──┐ │  │ •Search(TFIDF│  │ •Token mgmt   │  │
│  │  ├─Fallback┤ │  │ •Eligibility │  │ •Role-based    │  │
│  │  └─Mock────┘ │  │ •Grievance   │  │ •Dependencies  │  │
│  └─────────────┘  │ •DataLoader  │  └────────────────┘  │
│                    └──────────────┘                       │
│  ┌──────────────────────────────────────────────────┐    │
│  │              API Routes (/api/v1)                │    │
│  │  /schemes /services /eligibility /assistant      │    │
│  │  /grievance /directory /documents /admin /auth   │    │
│  └──────────────────────────────────────────────────┘    │
│  ┌──────────────────────────────────────────────────┐    │
│  │         JSON File-Based Data Store               │    │
│  │  schemes.json  services.json  departments.json   │    │
│  │  grievances.json  users.json  audit_log.json     │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- A Gemini API key (optional — falls back to local mode without it)

### 1. Clone and Setup Backend

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY (optional)
```

### 3. Start Backend Server

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Open Frontend

Open `frontend/index.html` in your browser, or serve it:

```bash
cd frontend
python -m http.server 3000
```

Then visit: **http://localhost:3000**

### 5. Run Tests

```bash
cd backend
python -m pytest tests/ -v
```

---

## 📁 Project Structure

```
MahaSeva AI Pro/
├── backend/
│   ├── requirements.txt
│   ├── .env.example
│   └── app/
│       ├── main.py              # FastAPI entry point
│       ├── config.py            # Settings & configuration
│       ├── ai/
│       │   ├── providers/       # AI provider abstraction
│       │   │   ├── base_provider.py
│       │   │   ├── gemini_provider.py
│       │   │   ├── fallback_provider.py
│       │   │   └── mock_provider.py
│       │   └── services/        # AI service orchestration
│       │       ├── assistant_service.py
│       │       ├── document_service.py
│       │       └── translation_service.py
│       ├── auth/                # JWT authentication
│       ├── core/                # Business logic engines
│       │   ├── data_loader.py
│       │   ├── search_engine.py
│       │   ├── eligibility_engine.py
│       │   └── grievance_manager.py
│       ├── models/schemas.py    # Pydantic v2 models
│       ├── api/v1/              # API route handlers
│       ├── data/                # Government data (JSON)
│       └── db/                  # File-based persistence
├── frontend/
│   ├── index.html               # SPA shell
│   ├── css/style.css            # Complete responsive CSS
│   └── js/
│       ├── app.js               # Routing, API layer, init
│       ├── components.js        # Reusable UI components
│       ├── i18n.js              # Trilingual translations
│       ├── schemes.js           # Scheme explorer
│       ├── services.js          # Service guide
│       ├── eligibility.js       # Eligibility checker
│       ├── assistant.js         # AI chat interface
│       ├── grievance.js         # Grievance portal
│       ├── directory.js         # Department/district directory
│       └── admin.js             # Admin dashboard
├── scripts/                     # Startup & utility scripts
├── docs/                        # Documentation
└── README.md
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/schemes` | List all schemes |
| GET | `/api/v1/schemes/{id}` | Scheme detail |
| GET | `/api/v1/services` | List all services |
| GET | `/api/v1/services/{id}` | Service detail |
| POST | `/api/v1/eligibility/check` | Check eligibility |
| POST | `/api/v1/assistant/ask` | AI Q&A |
| POST | `/api/v1/grievance/submit` | File grievance |
| GET | `/api/v1/grievance/track/{token}` | Track grievance |
| GET | `/api/v1/directory/departments` | List departments |
| GET | `/api/v1/directory/districts` | List districts |
| POST | `/api/v1/documents/analyze` | Analyze document |
| GET | `/api/v1/admin/dashboard` | Admin stats |
| GET | `/health` | System health |

---

## 🌐 Language Support

| Language | Status |
|----------|--------|
| English | ✅ Full support |
| मराठी (Marathi) | ✅ Full support |
| हिंदी (Hindi) | ✅ Full support |

---

## 🤖 AI Provider Architecture

```
AIProvider (Abstract)
├── GeminiProvider    — Real Gemini API integration
├── FallbackProvider  — Offline rule-based (no API needed)
└── MockProvider      — For automated testing
```

The system automatically falls back to local mode if no API key is configured or if the Gemini API is unavailable.

---

## 📊 Data Sources

All scheme and service data is sourced from publicly available Maharashtra Government Resolution (GR) documents and official portal information. Each entry includes the GR reference number for verification.

> **Important:** This prototype uses curated static datasets. In production, these would be synchronized with live government databases.

---

## ⚖️ Disclaimer

This is a **technology prototype** developed for demonstration purposes.

- **NOT** an official Government of Maharashtra portal
- **NOT** affiliated with or endorsed by any government department
- All government scheme information should be verified on official portals
- AI responses are generated from curated data and may not reflect the latest policy changes

**Official Portals:**
- [Aaple Sarkar](https://aaplesarkar.mahaonline.gov.in)
- [MahaDBT](https://mahadbt.maharashtra.gov.in)
- [MahaBhumi](https://mahabhumi.gov.in)

---

## 📜 License

MIT License — Free for educational and demonstration purposes.
