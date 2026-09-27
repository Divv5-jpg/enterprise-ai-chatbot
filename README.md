# Enterprise AI Chatbot

An agentic, tool-using chatbot built with **LangGraph** and **Groq**, demonstrating a progressive build-up from a basic conversational agent to a full-featured assistant with **Retrieval-Augmented Generation (RAG)**, **external tool calling**, **Model Context Protocol (MCP) integration**, and **persistent conversation memory** — all served through a **Streamlit** interface.

The repository is structured as a series of incremental backend/frontend pairs, each layering a new capability on top of the last, so the evolution of the architecture is visible directly in the codebase.

---

## ✨ Features

- **RAG / PDF retrieval** — ingests and retrieves context from PDF documents to ground responses in external knowledge. This is the flagship version of the project (`streamlit_rag_frontend.py` + `langgraph_rag_backend.py`).
- **Agentic conversation graph** — built with LangGraph's `StateGraph`, routing between an LLM node and a tool-execution node based on the model's own decisions (`tools_condition`).
- **Tool calling** — the agent can invoke:
  - Web search (DuckDuckGo)
  - Real-time stock price lookup (Alpha Vantage API)
  - External tools exposed via **MCP servers** (both `stdio` and `streamable_http` transports), using `langchain-mcp-adapters`
- **Persistent memory** — conversation state is checkpointed to **SQLite** (via `AsyncSqliteSaver`), enabling multi-threaded, resumable conversations across sessions.
- **Streaming responses** — a threaded streaming frontend for real-time token-by-token output.
- **Streamlit UI** — multiple frontend variants, each matched to a backend capability (base chat, database-backed, tool-augmented, RAG, MCP).

## 🏗️ Architecture

At its core, the chatbot is a LangGraph state machine:

```
START → chat_node → (tool call?) → tools → chat_node → ... → END
```

- `chat_node` invokes a Groq-hosted LLM (`ChatGroq`) bound to the available tool set.
- If the model requests a tool call, execution routes to a `ToolNode`; the result is fed back into `chat_node` for the next reasoning step.
- An async SQLite checkpointer persists the full message state per conversation thread, allowing past threads to be listed and resumed.
- A dedicated background event loop (via a daemon thread) bridges LangGraph's async APIs with Streamlit's synchronous execution model.

## 📁 Project Structure

| File | Description |
|---|---|
| `langgraph_backend.py` | Base conversational agent graph (no tools/memory). |
| `langgraph_backend_database.py` | Adds SQLite-backed checkpointing for persistent, resumable threads. |
| `langgraph_tool_backend.py` | Adds tool-calling capability (search, custom tools). |
| `langgraph_rag_backend.py` | Adds PDF ingestion and retrieval-augmented generation. |
| `langgraph_mcp_backend.py` | Adds MCP client integration for external tool servers, plus stock-price and search tools. |
| `streamlit_frontend.py` | Base Streamlit chat UI. |
| `streamlit_frontend_database.py` | Frontend for the database-backed backend, with thread history. |
| `streamlit_rag_frontend.py` | Frontend for PDF upload and RAG-based Q&A. |
| `streamlit_frontend_mcp.py` | Frontend for the MCP-enabled backend. |
| `streaming_frontend_threading.py` | Threaded/streaming response handling for real-time output. |
| `chatbot_async.py` | Async entry point / utilities for running the backend. |
| `11_tools.ipynb` | Notebook exploring and testing individual tool integrations. |

## 🛠️ Tech Stack

- **Orchestration:** LangGraph, LangChain Core
- **LLM Inference:** Groq (`langchain-groq`)
- **Tool Integration:** MCP (`langchain-mcp-adapters`), DuckDuckGo Search, Alpha Vantage API
- **Persistence:** SQLite (`aiosqlite`, `langgraph-checkpoint-sqlite`)
- **Frontend:** Streamlit
- **Language:** Python

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com)
- (Optional) An [Alpha Vantage API key](https://www.alphavantage.co) for stock price lookups

### Installation

```bash
git clone https://github.com/Divv5-jpg/enterprise-ai-chatbot.git
cd enterprise-ai-chatbot
python -m venv venv
source venv/bin/activate   # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

### Running the App

The primary entry point is the RAG-powered chatbot:

```bash
streamlit run streamlit_rag_frontend.py
```

Each backend also has its own matching Streamlit frontend, so you can run any stage of the project independently. For example, to run the MCP-enabled version instead:

```bash
streamlit run streamlit_frontend_mcp.py
```

## 🔭 Possible Extensions

- Swap SQLite checkpointing for a hosted Postgres/Redis store for multi-user deployment
- Add authentication and per-user thread isolation
- Expand the MCP tool registry with additional servers
- Add evaluation/observability (e.g., LangSmith tracing)

## 👤 Author

**Divya**
Integrated Dual Degree student, Biochemical Engineering, IIT (BHU) Varanasi

---

*This project was built to explore agentic AI system design — combining LLM orchestration, tool use, retrieval, and persistent memory into a single extensible chatbot framework.*
