<p align="center">
  <img src="assets/banner.svg" width="900" alt="CogniSync Banner">
</p>

<p align="center">
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT">
  </a>
  <img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python: 3.12+">
</p>

---

## 🧬 Abstract

**CogniSync** is a high-performance autonomous daemon engineered to bridge the gap between ephemeral human dialogue and structured intelligence. It operates as a silent observer, continuously distilling real-time conversation logs into a meticulously organized "Second Brain." 

By leveraging a sophisticated multi-pass cognitive pipeline, CogniSync ensures that every insight, decision, and solution is captured, deduplicated, and persisted—transforming raw text into actionable, long-term knowledge.

---

## 🛡️ Core Pillars

- **Autonomous Orchestration:** A zero-latency file watcher that monitors distributed conversation logs without human intervention.
- **Privacy-First Intelligence:** Localized data masking that redacts PII and sensitive credentials before they ever reach the AI processing layer.
- **Semantic Consolidation:** Intelligent merging logic that prevents knowledge fragmentation by unifying new insights with existing records.
- **Architectural Integrity:** Built on **Clean Architecture** principles, ensuring a modular, testable, and future-proof codebase.

---

## ⚙️ The Cognitive Pipeline

CogniSync employs a deterministic 4-pass pipeline to ensure maximum signal-to-noise ratio:

1.  **Distill (Compress):** Strips conversational overhead to produce dense, high-fidelity summaries.
2.  **Extract (Analyze):** Parallely identifies factual memories and complex problem-solution pairs.
3.  **Contextualize (Slug Match):** Resolves extracted entities against the existing knowledge graph using fuzzy-deterministic logic.
4.  **Synthesize (Consolidate):** Merges incremental updates into existing Knowledge Items (KIs), maintaining a unified source of truth.

---

## 📂 System Architecture

```bash
CogniSync/
├── src/
│   ├── config/         # System Foundation & Universal Path Resolution
│   ├── core/           # Domain Logic & State Orchestration
│   ├── services/       # Use Cases: 4-Pass Pipeline & Background Watcher
│   ├── providers/      # Interface Adapters: LLM & External Integrations
│   ├── schema/         # Data Contracts & Type Definitions
│   └── helpers/        # Cross-cutting Concerns: Masking & Logging
├── prompts/            # Expert-Level LLM Instruction Templates
├── tests/              # Comprehensive Unit & Integration Suite
├── main.py             # Unified CLI Controller
└── .env.example        # Environment Specification
```

---

## 🚀 Quick Start

### 1. Environment Synthesis
Clone the repository and prepare your environment:
```bash
git clone https://github.com/mdnaimul22/CogniSync.git
cd CogniSync
```

Initialize your `.env` file (Supports **Universal Path Resolution**):
```dotenv
# Universal Paths (Supports ~ expansion)
BRAIN_DIR=~/.gemini/antigravity/brain
KNOWLEDGE_DIR=~/.gemini/antigravity/knowledge

# LLM Specification
LLM_BASE_URL=http://<YOUR_LLM_HOST>/v1
LLM_MODEL=CohereForAI_C4AI_Command
```

### 2. Execution
Run the daemon in detached mode for continuous background synchronization:
```bash
screen -dmS cognisync python3 main.py watch
```

Monitor system health and knowledge density:
```bash
python3 main.py status
```

---

## 🤝 Contributing

We welcome contributions that push the boundaries of autonomous knowledge management. 

1.  **Fork** the repository.
2.  **Branch:** `git checkout -b feature/Optimization`.
3.  **Commit:** Adhere to conventional commit messages.
4.  **Push:** `git push origin feature/Optimization`.
5.  **PR:** Open a Pull Request for architectural review.

---

<p align="center">
  <i>"Precision is not an accident; it is the deliberate application of strict standards."</i>
</p>
