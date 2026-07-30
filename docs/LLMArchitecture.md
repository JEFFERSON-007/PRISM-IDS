# AI Security Analyst (LLM Integration) Architecture

The AI Security Analyst is an explanatory intelligence module integrated into the PRISM IDS FastAPI Server.

## Architecture Workflow

```
Hybrid Detection Engine
          ↓
     Risk Engine
          ↓
   Alert Database
          ↓
  LLM Context Builder  ── (Sanitizes 5-tuple, rules, & ML probabilities)
          ↓
   Prompt Builder     ── (Applies Jinja2 security templates)
          ↓
    Ollama Client     ── (Communicates via HTTPX to Ollama API: qwen:3b / llama3.2)
          ↓
  Response Parser     ── (Validates JSON DTO: Executive summary, MITRE ATT&CK, Remediations)
          ↓
 SOC React Dashboard
```

## Key Architectural Principles

1. **Non-Authoritative Role**: The LLM does NOT detect threats or alter firewall rules directly. Primary detection remains 100% authoritative under the Hybrid Detection Engine.
2. **Resilient Fallback**: If local Ollama service is offline or inference times out, the `LLMService` utilizes the `RecommendationEngine` to return rule-based MITRE ATT&CK mappings and prioritized mitigation steps without failing.
3. **Structured Pydantic Contract**: Enforces valid JSON payloads matching `LLMAnalysisResponse`.
