# Prompt Template Guide

All prompt templates are located inside `app/llm/prompt_builder.py`.

## Adding Custom Prompt Templates

1. Define system prompt constant in `PromptBuilder`.
2. Add static helper method taking formatted `alert_context` DTO dictionary.
3. Ensure template explicitly requests structured JSON output format matching Pydantic schemas.
