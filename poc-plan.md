# PoC Plan: TradingAgents-Studio

## Project Classification
- **Type:** llm-app
- **Key Technologies:** Python, FastAPI, Vue 3, LangGraph, LangChain, WebSocket, SQLite
- **ODH Relevance:** Demonstrates multi-agent LLM orchestration as a containerized web service on OpenShift, validating agentic architecture patterns for platform teams.

## PoC Objectives
1. Validate that the FastAPI backend with LangGraph agent orchestration runs reliably in a UBI-based container on OpenShift
2. Confirm the Vue 3 frontend builds and is served correctly through the backend's static file mounting
3. Verify WebSocket connectivity works through OpenShift routing
4. Demonstrate the health check and API endpoints are accessible

## Infrastructure Requirements
- **Resource Profile:** medium (1Gi RAM, 500m CPU - LLM calls are external API calls, not local inference)
- **GPU Required:** No
- **Persistent Storage:** None (SQLite in-memory/ephemeral is sufficient for PoC)
- **Sidecar Containers:** None
- **LLM API Required:** Yes - needs OpenAI-compatible API endpoint
- **LLM Env Pattern:** langchain (uses OPENAI_API_KEY and OPENAI_BASE_URL)

## Test Scenarios

### Scenario 1: Health Check
- **Description:** Verify the FastAPI server starts and responds to health checks
- **Type:** http
- **Endpoint:** /api/health
- **Expected:** Returns 200 with `{"status": "ok"}`
- **Timeout:** 60 seconds

### Scenario 2: API Root Access
- **Description:** Verify the root path serves the frontend SPA or returns a valid response
- **Type:** http
- **Endpoint:** /
- **Expected:** Returns 200 (either frontend HTML or FastAPI redirect)
- **Timeout:** 30 seconds

### Scenario 3: History API
- **Description:** Verify the history API endpoint returns a valid response
- **Type:** http
- **Endpoint:** /api/history
- **Expected:** Returns 200 with JSON array (empty or with data)
- **Timeout:** 30 seconds

### Scenario 4: Settings API
- **Description:** Verify the settings/configuration endpoint works
- **Type:** http
- **Endpoint:** /api/settings
- **Expected:** Returns 200 with JSON configuration object
- **Timeout:** 30 seconds

## Dockerfile Considerations
- Use multi-stage build: Node.js stage to build Vue 3 frontend, Python stage for backend
- Frontend dist files must be placed at `web/frontend/dist/` for the backend to serve them
- Backend listens on port 8080 (remapped from 8000 for OpenShift compatibility)
- Install `web` extras: `pip install -e ".[web,cn]"`
- Set `TRADINGAGENTS_LOG_DIR` to a writable directory

## Deployment Considerations
- **Deployment Model:** deployment (long-running web server)
- **Listens on Port:** 8080
- **Service:** ClusterIP exposing port 8080
- **Environment Variables:** OPENAI_API_KEY (secret), OPENAI_BASE_URL (via LLM proxy)
- **Test Strategy:** http
