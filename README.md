# 👼 Talent Angel — AI-Powered Career Strategist

> Building the future of career transitions using **LangGraph**, **Neo4j GraphRAG**, and **Gemini 2.5**.

Talent Angel is an agentic career guidance system designed to help professionals (e.g., teachers, researchers) transition into high-growth tech roles (e.g., Technical Writing, Data Science). By leveraging the **O\*NET database** and a **Knowledge Graph**, the agent calculates skill gaps and generates market-aware career roadmaps.

---

## 🚀 Features

- **Graph-RAG Architecture** — Uses Neo4j to store and retrieve complex relationships between occupations, skills, and market trends.
- **Agentic Multi-Node Workflow** — Powered by LangGraph with the following pipeline:
  - `Gatekeeper` — Validates and secures user input.
  - `Locator` — Maps the user to an "Anchor Career" in the graph.
  - `Connector` — Fetches graph-based relationships.
  - `Pathfinder` — Calculates the precise skill gap between Point A and Point B.
  - `Consultor` — Generates high-impact, strategic roadmaps.
  - `Critic` — Validates the response for accuracy and depth.
- **Vector Search** — Integrated Neo4j Vector Index for semantic occupation matching.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangChain / LangGraph |
| Database | Neo4j AuraDB (Graph + Vector) |
| LLM | Google Gemini 2.5 Flash / Pro |
| Data Source | O\*NET OnLine (Occupational Information Network) |
| Runtime | Python 3.13+ |

---

## 📁 Project Structure

```
POC-LFDT/
├── config/
│   ├── prompts.yaml              # System instructions for all agent nodes
│   └── settings.py               # Project-wide configuration
├── data/
│   └── raw/onet/
│       ├── Occupation Data.txt
│       ├── Skills.txt
│       └── Task Statements.txt
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_graph_ingestion_test.ipynb
│   └── 03_agent_prototyping.ipynb
├── src/
│   ├── agents/
│   │   ├── graph.py              # LangGraph workflow definition
│   │   ├── nodes.py              # Logic for each agent node
│   │   └── state.py              # Graph state schema
│   ├── database/
│   │   └── neo4j_driver.py       # Connection & Vector store initialization
│   ├── ingestion/
│   │   ├── loader.py             # O*NET data processing
│   │   └── vectorizer.py         # Embedding logic
│   ├── retrieval/
│   │   ├── hybrid_retriever.py
│   │   ├── simple_retriever.py   # Cypher and Vector search logic
│   │   └── text2cypher.py
│   └── utils/
│       ├── helpers.py
│       └── llms.py               # LLM model initializations
├── tests/
│   ├── test_agents.py
│   └── test_graph.py
├── run_chat.py                   # Main CLI entry point
├── run_ingestion.py              # Script to populate the Neo4j graph
├── test_setup.py
├── requirements.txt
└── .env                          # API keys and environment variables
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

- A [Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database/) instance (Free Tier works).
- A [Google AI Studio](https://aistudio.google.com/) API Key.

### 2. Clone and Environment Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/POC-LFDT.git
cd POC-LFDT

# Create a virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY="your_gemini_key"
NEO4J_URI="neo4j+s://your-id.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_password"
```

---

## 🏗️ Execution Flow

### Phase 1 — Data Ingestion

Populate the graph database with O\*NET data before running the agent:

```bash
python run_ingestion.py
```

This script will:
- Parse text files from `data/raw/onet/`
- Generate embeddings for occupations
- Create `Occupation` and `Skill` nodes with `REQUIRES` relationships in Neo4j

### Phase 2 — Start the Agent

Launch the interactive CLI:

```bash
python run_chat.py
```

---

## 🛡️ API Usage & Rate Limit Notes

This project uses a multi-node LangGraph structure. If you are on the **Gemini Free Tier** (15–20 RPM limit), you may encounter `429 Resource Exhausted` errors.

Mitigations already in place:

- **Rate Limiting** — Small delays between node transitions in `nodes.py`.
- **Hardcoded Dimensions** — Embedding dimension is set to `768` in `neo4j_driver.py` to skip redundant test calls on startup.

> 💡 For production testing, it is recommended to use the **Pay-as-you-go** tier in Google AI Studio.

---

## 📄 License

This project is open-source. See `LICENSE` for details.