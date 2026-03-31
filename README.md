# 🧭 CareerForge AI — Intelligent Career Transition Engine

> An AI-powered career strategist that helps professionals navigate complex career transitions using **LangGraph**, **Neo4j GraphRAG**, and **Google Gemini 2.5**.

---

## 🌟 What is CareerForge AI?

CareerForge AI is a fully agentic career guidance system built for professionals who want to transition into high-growth tech roles. Whether you're a **teacher moving into Technical Writing**, a **researcher pivoting to Data Science**, or any professional looking to reinvent their career — CareerForge AI analyses your current skills, identifies the exact gaps, and builds a strategic, step-by-step roadmap tailored just for you.

Unlike generic career advice tools, CareerForge AI is grounded in **real occupational data from the O\*NET database** — the gold standard for occupational information in the US — combined with a **Neo4j Knowledge Graph** that understands how jobs, skills, and market trends relate to each other. The result is actionable, precise, and intelligent career guidance at scale.

---

## 🚀 Key Features

### 🔗 Graph-RAG Architecture
CareerForge AI uses a **Graph Retrieval-Augmented Generation (Graph-RAG)** approach powered by Neo4j. Rather than relying on flat document retrieval, the system queries a rich knowledge graph of occupations, skills, and their interconnections — enabling far more contextual and accurate responses than traditional RAG systems.

### 🤖 Multi-Node Agentic Workflow
The system is built on **LangGraph** and orchestrates a pipeline of specialized AI agents, each with a distinct responsibility:

| Agent | Role |
|---|---|
| `Gatekeeper` | Validates and sanitizes user input before processing |
| `Locator` | Semantically maps the user's current role to an "Anchor Career" in the graph |
| `Connector` | Traverses the knowledge graph to fetch related occupations and skill clusters |
| `Pathfinder` | Computes the precise skill gap between the user's current position and target role |
| `Consultor` | Synthesizes all data into a high-impact, prioritized career roadmap |
| `Critic` | Reviews the generated roadmap for accuracy, depth, and actionability |

This pipeline ensures every response is not just generated — but **validated and refined** before reaching the user.

### 🔍 Semantic Vector Search
Integrated **Neo4j Vector Index** enables semantic search over occupations. Even if a user describes their job in informal language, the system intelligently matches it to the correct O\*NET occupation using embedding-based similarity search.

### 🧩 Hybrid Retrieval
The `hybrid_retriever.py` combines both **Cypher graph queries** and **vector similarity search**, giving the best of structured and semantic retrieval for highly relevant results.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Orchestration | LangChain / LangGraph | Agent workflow & state management |
| Database | Neo4j AuraDB | Knowledge graph + vector store |
| LLM | Google Gemini 2.5 Flash / Pro | Natural language reasoning |
| Data Source | O\*NET OnLine | Occupational skills & task data |
| Embeddings | Google Generative AI Embeddings | Semantic vector search (768-dim) |
| Runtime | Python 3.13+ | Core application runtime |

---

## 📁 Project Structure

```
careerforge-ai/
├── config/
│   ├── prompts.yaml              # System prompts & instructions for all agent nodes
│   └── settings.py               # Centralized project-wide configuration
│
├── data/
│   └── raw/onet/                 # Raw O*NET source files
│       ├── Occupation Data.txt   # List of all occupations with SOC codes
│       ├── Skills.txt            # Skills mapped to each occupation
│       └── Task Statements.txt   # Task-level descriptions per occupation
│
├── notebooks/                    # Exploratory & prototyping notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_graph_ingestion_test.ipynb
│   └── 03_agent_prototyping.ipynb
│
├── src/
│   ├── agents/
│   │   ├── graph.py              # LangGraph workflow definition & node wiring
│   │   ├── nodes.py              # Business logic for each agent node
│   │   └── state.py              # Shared graph state schema (TypedDict)
│   │
│   ├── database/
│   │   └── neo4j_driver.py       # Neo4j connection, vector store & index setup
│   │
│   ├── ingestion/
│   │   ├── loader.py             # Parses & cleans O*NET raw text files
│   │   └── vectorizer.py         # Generates and stores occupation embeddings
│   │
│   ├── retrieval/
│   │   ├── hybrid_retriever.py   # Combines vector + Cypher graph retrieval
│   │   ├── simple_retriever.py   # Standalone Cypher & vector search logic
│   │   └── text2cypher.py        # Converts natural language to Cypher queries
│   │
│   └── utils/
│       ├── helpers.py            # Shared utility functions
│       └── llms.py               # LLM & embedding model initializations
│
├── tests/
│   ├── test_agents.py            # Unit tests for agent nodes
│   └── test_graph.py             # Integration tests for the graph workflow
│
├── run_chat.py                   # 🚀 Main CLI entry point
├── run_ingestion.py              # 📥 Populates the Neo4j knowledge graph
├── test_setup.py                 # Verifies environment & connection setup
├── requirements.txt              # Python dependencies
└── .env                          # API keys and environment variables (not committed)
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites

Before getting started, make sure you have the following ready:

- A **[Neo4j Aura](https://neo4j.com/cloud/platform/aura-graph-database/)** instance — the Free Tier is sufficient to get started.
- A **[Google AI Studio](https://aistudio.google.com/)** API Key for Gemini access.
- **Python 3.13+** installed on your machine.

### 2. Clone the Repository

```bash
git clone https://github.com/yourusername/careerforge-ai.git
cd careerforge-ai
```

### 3. Create a Virtual Environment

```bash
# Create the environment
python -m venv venv

# Activate on Linux/macOS
source venv/bin/activate

# Activate on Windows
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory and fill in your credentials:

```env
GOOGLE_API_KEY="your_gemini_api_key"
NEO4J_URI="neo4j+s://your-instance-id.databases.neo4j.io"
NEO4J_USERNAME="neo4j"
NEO4J_PASSWORD="your_neo4j_password"
```

### 6. Verify Your Setup

Run the setup test to confirm all connections are working before proceeding:

```bash
python test_setup.py
```

---

## 🏗️ How to Run

### Phase 1 — Data Ingestion (Run Once)

Before launching the agent, you need to populate the Neo4j knowledge graph with O\*NET data. This is a one-time setup step:

```bash
python run_ingestion.py
```

This script will:
- Parse and clean occupation, skills, and task data from `data/raw/onet/`
- Generate vector embeddings for each occupation using Gemini embeddings
- Create `Occupation` and `Skill` nodes in Neo4j
- Build `REQUIRES` relationships between occupations and their skills
- Initialize the Neo4j Vector Index for semantic search

> ⏱️ Ingestion may take a few minutes depending on data size and API response times.

### Phase 2 — Start a Career Consultation

Once ingestion is complete, launch the interactive CLI agent:

```bash
python run_chat.py
```

You'll be prompted to describe your current role and target career. The multi-node pipeline will then analyse your profile, compute your skill gap, and generate a personalized roadmap.

---

## 🛡️ API Usage & Rate Limit Notes

CareerForge AI makes multiple sequential LLM calls per user query due to its multi-node architecture. If you're using the **Gemini Free Tier** (limited to 15–20 requests per minute), you may occasionally see `429 Resource Exhausted` errors.

The following mitigations are already built into the project:

- **Automatic Rate Limiting** — Deliberate delays are inserted between node transitions in `nodes.py` to stay within quota limits.
- **Hardcoded Embedding Dimensions** — The embedding dimension is fixed at `768` in `neo4j_driver.py`, eliminating unnecessary test API calls during startup.

> 💡 For smoother production-level testing, switching to the **Pay-as-you-go** tier in Google AI Studio is strongly recommended.

---


## 📄 License

This project is open-source. See `LICENSE` for full details.