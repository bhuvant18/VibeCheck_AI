# 🛡️ VibeCheck AI - The AI Hallucination Detector

A **"Truth Layer"** application that detects and corrects AI-generated hallucinations using Google's Gemini 2.0 Flash with Search Grounding and Semantic Scholar for academic citation verification.

![VibeCheck Architecture](docs/architecture.png)

## 🎯 Features

- **Real-time Fact Verification**: Uses Google Search Grounding to verify claims against live web sources
- **Academic Citation Checker**: Validates paper citations using Semantic Scholar's 200M+ paper database  
- **Visual "Redline" UI**: Green highlighting for verified facts, red for hallucinations
- **One-Click Auto-Fix**: Automatically corrects false claims with factual information
- **Structured Output**: Returns clean JSON with status, reasoning, corrections, and source URLs

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VibeCheck AI                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌──────────────────────────────────┐  │
│  │    React     │ ──────> │         FastAPI Backend          │  │
│  │   Frontend   │ <────── │                                  │  │
│  └──────────────┘         │  ┌────────────────────────────┐  │  │
│                           │  │     Gemini 2.0 Flash       │  │  │
│                           │  │  (Single-Shot Structured)  │  │  │
│                           │  │                            │  │  │
│                           │  │  Tools:                    │  │  │
│                           │  │  • Google Search Grounding │  │  │
│                           │  │  • Semantic Scholar API    │  │  │
│                           │  └────────────────────────────┘  │  │
│                           └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Google Cloud Project with Vertex AI API enabled, OR
- Google AI Studio API Key

### 1. Clone & Install

```bash
cd vibecheck
pip install -r requirements.txt
```

### 2. Configure Authentication

**Option A: Vertex AI (Recommended for ADK)**
```bash
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # optional
```

**Option B: Gemini API Key**
```bash
export GEMINI_API_KEY="your-api-key"
```

### 3. Start the Backend

```bash
cd backend
python api.py
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`

### 4. Start the Frontend

```bash
cd frontend-react
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`

## 📚 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/api/verify` | POST | Main text verification endpoint |
| `/api/check-citation` | POST | Direct citation verification |
| `/api/batch-verify` | POST | Batch verification (up to 5 texts) |

### Example Request

```bash
curl -X POST http://localhost:8000/api/verify \
  -H "Content-Type: application/json" \
  -d '{"text": "The moon is made of green cheese."}'
```

### Example Response

```json
{
  "claims": [
    {
      "original_text": "The moon is made of green cheese.",
      "type": "FACT",
      "status": "HALLUCINATION",
      "reasoning": "Scientific evidence shows the Moon is composed of rock and regolith, not cheese.",
      "correction": "The Moon is composed primarily of silicate rocks and metal.",
      "source_url": "https://science.nasa.gov/moon/",
      "confidence_score": 95
    }
  ]
}
```

## 🎨 UI Features

1. **Input Panel**: Paste any AI-generated text
2. **Audit Button**: Triggers verification with visual progress
3. **Redline View**: 
   - 🟢 Green = Verified facts with source links
   - 🔴 Red = Hallucinations with corrections
   - 🟡 Yellow = Suspicious (needs review)
4. **Auto-Fix Button**: One-click correction of all hallucinations

## 🔧 Project Structure

```
vibecheck/
├── backend/
│   ├── agent.py          # Core verification logic
│   ├── api.py            # FastAPI server
│   └── requirements.txt  # Backend dependencies
├── frontend/
│   ├── app.py            # Streamlit UI
│   └── requirements.txt  # Frontend dependencies
├── requirements.txt      # All dependencies
├── .env.example          # Environment template
└── README.md
```

## 🧪 Testing

### Test with Sample Hallucinated Text

```python
test_text = """
Recent studies by Johnson et al. (2024) in the Journal of Advanced AI 
suggest that neural networks consume 50% less energy when trained on 
quantum hardware. The moon is made of green cheese, confirmed by NASA.
The Transformer architecture was introduced by Vaswani et al. in 2017.
"""
```

Expected results:
- ❌ "Johnson et al. (2024)" → HALLUCINATION (fake citation)
- ❌ "moon is made of green cheese" → HALLUCINATION (false claim)
- ✅ "Vaswani et al. (2017)" → VERIFIED (real paper)

## 🏆 Why This Architecture Wins

1. **Uses Google's Flagship Feature**: Search Grounding is Google's key differentiator for reducing hallucinations
2. **Single-Shot Efficiency**: One API call instead of multi-agent chains (5s vs 40s response time)
3. **Structured Output**: Pydantic schema forces reliable JSON, ready for UI rendering
4. **Dual Verification**: Combines web search + academic database for comprehensive coverage
5. **Human-in-the-Loop**: Shows problems first, lets user approve fixes (builds trust)

## 📝 License

MIT License - Built for the AI Hackathon 2026

## 🙏 Credits

- [Google Gemini 2.0](https://ai.google.dev/) - Core AI with Search Grounding
- [Semantic Scholar API](https://www.semanticscholar.org/) - Academic citation verification
- [Streamlit](https://streamlit.io/) - Frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
