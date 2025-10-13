# Summary

This project shows how to build **durable AI agents** using four production-grade components:

- [Mistral AI SDK](https://github.com/mistralai/client-python) — Mistral LLMs and agent API
- [Temporal Python SDK](https://github.com/temporalio/sdk-python) — durable workflows, retries, and long-running tasks
- [Model Context Protocol (MCP)](https://github.com/modelcontextprotocol/python-sdk) — standard interface for tools and data sources
- **(Optional)** [Pydantic Logfire](https://pydantic.dev/logfire) — unified observability (logs, traces, metrics) with native LLM & agent instrumentation


# 1. Set up your Python environment
```
uv sync
source .venv/bin/activate
```

# 2. Run the MCP FastAPI Server on a custom port
In this example, we package the prompts and tools of [the food diet agent](https://github.com/mistralai/cookbook/tree/main/mistral/agents/agents_api/food_diet_companion) in an MCP server.
```
export PYTHONPATH=.
uv run uvicorn mcp_server.main:app --reload --port 9000
```

```bash
brew install temporal
temporal server start-dev
```

# 4. Start a Temporal worker
Execute the following command to start a worker to run the examples. 
Ensure that all your environment variables reside at file .env.

```bash
export PYTHONPATH=.
uv run --env-file .env tasks/worker.py
```
