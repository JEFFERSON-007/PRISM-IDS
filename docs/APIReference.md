# LLM API Reference Specification

## Endpoints

### 1. Alert Security Briefing
- **`POST /api/v1/llm/analyze`**
- **Headers**: `Authorization: Bearer <jwt>`
- **Request Body**:
  ```json
  {
    "alert_id": "ALT-2026-0001"
  }
  ```
- **Response**: `LLMAnalysisResponse` (Executive summary, technical explanation, MITRE ATT&CK mapping, prioritized remediations).

### 2. Analyst Q&A Chat Session
- **`POST /api/v1/llm/chat`**
- **Headers**: `Authorization: Bearer <jwt>`
- **Request Body**:
  ```json
  {
    "session_id": "sess-123",
    "message": "Why did this alert trigger on port 80?",
    "alert_id": "ALT-2026-0001"
  }
  ```
- **Response**: `ChatMessageResponse` (Reply text, timestamp, model used).

### 3. LLM Service Health Check
- **`GET /api/v1/llm/health`**
- **Response**: `LLMHealthResponse` (Status, Ollama URL, configured model, online boolean).
