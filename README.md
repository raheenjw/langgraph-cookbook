# LangGraph Tutorials

This repository is a comprehensive collection of tutorials, examples, and ready-to-use applications for learning **LangGraph**. LangGraph is a powerful library built for creating stateful, multi-actor applications with Large Language Models (LLMs), enabling complex workflows like cycles, persistence, and human-in-the-loop interactions.

## 📂 Repository Structure

The core of this repository is organized into several key areas:

### 1. 🎓 Tutorials (`tutorials/`)
Foundational concepts and examples to get you started with LangGraph.
- **tools.ipynb (`tutorials/tools.ipynb`)**: A Jupyter notebook focused on integrating and using custom tools within LangChain/LangGraph.
- **workflows.ipynb (`tutorials/workflows.ipynb`)**: Exploration of different LangGraph workflow patterns and configurations.
- **langgraph_tutorial.py (`tutorials/langgraph_tutorial.py`)**: Introduction to building a basic chatbot with state management.
- **langgraph_tutorial2.py (`tutorials/langgraph_tutorial2.py`)**: A more advanced router agent implementation that classifies user intent (Emotional vs. Logical) and routes queries accordingly.

### 2. 🌐 Streamlit Applications
Interactive web interfaces for the LangGraph agents.
- **`chatbot_streamlit/`**: A clean Streamlit frontend for interacting with a basic LangGraph chatbot.
- **`chatbot_streamlit_with_db/`**: An enhanced version of the Streamlit app that includes **SQLite persistence** for maintaining chat history across sessions.

### 3. 🛠️ MCP Integration (`mcp-server/`)
Examples of using the **Model Context Protocol (MCP)** to give agents access to local tools.
- **`chatbot_mcp.py`**: An AI agent that leverages MCP to communicate with a local tool server.
- **`expense_tracker.py`**: A sample MCP server implementing an expense tracking tool with a local SQLite database.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Environment Variables**: Create a `.env` file in the root directory with the following:
  ```env
  ANTHROPIC_API_KEY=your_anthropic_api_key
  OPENAI_API_KEY=your_openai_api_key
  ```
- **Ollama**: If not using the above, we can use ollama for local model usage like Llama3.2

### Installation

It is recommended to use a virtual environment. This repository uses `uv` for dependency management, but you can also use `pip`.

```bash
# Using uv (recommended)
uv sync

# Using pip
pip install -r requirement.txt
```

---

## 📖 Usage Guide

### 1. Running Basic Tutorials
Explore the fundamentals by running the scripts in the `tutorials/` directory:
```bash
python tutorials/langgraph_tutorial.py
python tutorials/langgraph_tutorial2.py
```

### 2. Launching Streamlit Web Apps
To interact with the agents via a browser:
```bash
# Basic Chatbot
streamlit run chatbot_streamlit/frontend.py

# Chatbot with History Persistence
streamlit run chatbot_streamlit_with_db/frontend.py
```

### 3. MCP Expense Tracker Demo
First, ensure Ollama is running, then execute the MCP agent:
```bash
python mcp-server/chatbot_mcp.py
```
*Tip: Try saying "I spent 200 on dinner today" and then "Show my total expenses".*

---

## 🐳 Docker Support
A `docker-compose.yml` is located in the `tutorials/` directory for setting up a Postgres database, which can be used for advanced LangGraph persistence and checkpointing.

```bash
cd tutorials
docker-compose up -d
```

---

## 🔗 Learn More
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Anthropic API Documentation](https://docs.anthropic.com/)
