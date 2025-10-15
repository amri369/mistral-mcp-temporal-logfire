# Durable Stateful Agents with Mistral + Temporal + MCP

<p align="left">
  <img src="assets/architecture.png" alt="System Architecture" width="50%">
</p>

Production-ready agent architecture combining **Mistral's server-side stateful agents** with **Temporal's durable execution** and **MCP's standardized tool interface**. This setup handles long-running tasks, automatic retries, and maintains conversation state across failures.

## Architecture

**Core Stack:**
- **Mistral AI Agent API** – Server-side stateful agents; register agents on Mistral's infrastructure, update configurations, and run multi-turn conversations with persistent state managed by Mistral
- **Temporal Workflows** – Durable orchestration; activities auto-retry on failure, workflows resume from last checkpoint
- **MCP Server** – Exposes tools and prompts over HTTP/SSE; agents discover capabilities at runtime
- **Logfire** *(optional)* – OpenTelemetry-native observability; auto-instruments FastAPI endpoints and Mistral agent calls with full request/response traces

**Key Design Decisions:**
1. **Mistral hosts agent state server-side** – unlike traditional stateless LLM APIs, Mistral's Agent API maintains agent definitions and conversation history on their servers; you register agents once, then interact via agent_id
2. **Temporal workflows orchestrate agent interactions** – workflow state persists locally while Mistral manages agent/conversation state remotely; workflows survive crashes and coordinate multi-step agent tasks
3. **Tools packaged as MCP resources** – agents dynamically fetch available tools via `list_tools()`, no hardcoded function definitions
4. **FastAPI orchestrates requests** – receives user queries, triggers Temporal workflows, streams responses
5. **Async context managers** – MCP client sessions properly cleanup SSE connections
6. **Logfire instruments the entire request path** – captures FastAPI route traces, Mistral API calls with token usage, and correlates them in a unified trace view

**Data Flow:**
```
User Request → FastAPI → Temporal Workflow → Mistral Agent API (stateful)
      ↓            ↓              ↓                  ↓
   Logfire ←──────┴──────────────┴──────────────────┘
                                         ↓
                                 MCP Server (tools/prompts)
                                         ↓
                                 Execute tool activities
                                         ↓
                                 Stream response → User
```

## Quick Start

### 1. Environment Setup
```bash
uv sync
source .venv/bin/activate
```

### 2. Launch MCP Server
Serves the [food diet companion agent](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/food_diet_companion) tools and prompts:
```bash
export PYTHONPATH=.
uv run uvicorn mcp_server.main:app --reload --port 9000
```

### 3. Start Temporal Dev Server
```bash
brew install temporal
temporal server start-dev
```

### 4. Start FastAPI Gateway
```bash
export PYTHONPATH=.
uv run uvicorn api.main:app --reload
```

### 5. Run Temporal Worker
Executes workflow and activity tasks. Requires `.env` with `MISTRAL_API_KEY`:
```bash
export PYTHONPATH=.
uv run --env-file .env tasks/worker.py
```

### 6. Test the Agent
```bash
export PYTHONPATH=.
uv run --env-file .env examples/main.py
```

**API:**
OpenAPI docs at http://localhost:8000/docs

## Why This Stack?

- **Mistral's stateful agents** are unique among LLM providers; agents are registered and managed server-side, eliminating the need to pass full conversation history with every request
- **Temporal** handles transient failures (API timeouts, rate limits) with automatic retries and orchestrates complex multi-agent workflows
- **MCP** decouples tool implementation from agent logic; swap tool providers without changing agent code
- **Logfire** provides unified view of workflow executions, LLM calls (with prompts, completions, token counts), and FastAPI request lifecycle in production