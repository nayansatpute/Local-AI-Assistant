🤖 Local AI Assistant

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Ollama](https://img.shields.io/badge/Ollama-Local_LLM-black?logo=ollama)
![Pydantic](https://img.shields.io/badge/Pydantic-Validation-red)
![Streamlit](https://img.shields.io/badge/Streamlit-UI-ff4b4b?logo=streamlit)
![License](https://img.shields.io/badge/License-MIT-green)

A three-phase local AI inference system that runs Small Language Models (SLMs) entirely offline — addressing data privacy, latency, and cost constraints without any cloud API dependency.

> Built and benchmarked on 8GB RAM with CPU-only inference (Intel UHD Graphics).

---

📸 Demo

![Chat UI](screenshots/chat_ui.png)

---

🏗️ Project Architecture
local-ai-assistant/
├── phase1_benchmarking/       # Performance measurement pipeline
│   ├── benchmark.py
│   └── results/
├── phase2_reliability/        # Schema enforcement + retry logic
│   ├── schemas.py
│   └── reliable_client.py
├── phase3_comparison/         # Model comparison study
│   ├── compare_models.py
│   └── results/
└── app.py                     # Streamlit chat interface


---

## 🔬 Phase 1 — Benchmarking

Measured real inference performance on consumer hardware using Ollama.

**Key Metrics Captured:**
- **TTFT** (Time to First Token) — latency before response begins
- **Tokens/sec** — generation throughput
- **Cold vs Warm start** — memory loading behavior

**Results on llama3.2:3b (CPU-only):**

| Run | TTFT (s) | Tokens/sec | Total (s) |
|-----|----------|------------|-----------|
| 1 (cold) | 8.678 | 5.4 | 17.84 |
| 2 (warm) | 0.374 | 10.4 | 10.04 |
| 3 (warm) | 0.349 | 10.4 | 11.87 |
| **AVG** | **3.134** | **8.7** | **13.25** |

**Finding:** Cold start is 23x slower than warm start due to model loading into RAM.

---

## 🛡️ Phase 2 — Reliability

Enforced structured JSON output using Pydantic schemas with automatic retry mechanisms.

**Schema Design:**
```python
class AIResponse(BaseModel):
    answer: str
    confidence: str        # high / medium / low
    key_points: list[str]  # exactly 3 points
    word_count: int
```

**Features:**
- JSON validation on every response
- Auto-retry up to 3 times on invalid output
- Markdown fence stripping for model quirks
- First-attempt success rate: ~95%

---

## 📊 Phase 3 — Model Comparison

Systematic head-to-head study comparing 1B vs 3B parameter models.

| Model | Avg TTFT | Avg tok/s | Avg Total | Verdict |
|-------|----------|-----------|-----------|---------|
| llama3.2:1b | 1.891s | **12.6** | 8.89s | ⚡ Fastest |
| llama3.2:3b | 3.333s | 7.6 | 14.01s | 📝 Most detailed |

**Engineering Conclusion:**
- 1B model is **65% faster** with **43% lower latency**
- On RAM-constrained hardware, llama3.2:1b is the optimal choice for real-time applications
- 3B model produces higher quality responses for accuracy-critical tasks

---

## 💬 Streamlit Chat UI

Interactive chat interface with real-time performance metrics on every response.

**Features:**
- 🟢 Offline badge — confirms no internet usage
- Model selector (switch between 1b and 3b)
- Temperature and max token controls
- Live token streaming with typing animation
- Per-response metrics (tok/s, TTFT, total time)
- Session stats tracking

**Run the app:**
```bash
streamlit run app.py
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- [Ollama](https://ollama.com) installed

### Installation

```bash
# Clone the repo
git clone https://github.com/nayansatpute/Local-AI-Assistant.git
cd Local-AI-Assistant

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Pull models
ollama pull llama3.2:3b
ollama pull llama3.2:1b
```

### Run Each Phase

```bash
# Phase 1 — Benchmark
python phase1_benchmarking/benchmark.py

# Phase 2 — Reliability
python phase2_reliability/reliable_client.py

# Phase 3 — Comparison
python phase3_comparison/compare_models.py

# Chat UI
streamlit run app.py
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.11 | Core language |
| Ollama | Local model serving |
| Pydantic | Schema validation |
| Streamlit | Chat UI |
| Rich | Terminal formatting |
| Pandas | Data analysis |

---

## 💻 Hardware Tested On

| Spec | Details |
|------|---------|
| RAM | 8GB |
| GPU | Intel UHD (CPU inference only) |
| OS | Windows 11 |

> This project is intentionally designed for constrained hardware.
> No GPU required.

---

## 📄 License

MIT License — free to use and modify.