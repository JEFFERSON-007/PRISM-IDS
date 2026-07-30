# Agent Security Architecture

## 1. Credentials Persistence

Issued `agent_id` and `secret_key` credentials are saved locally in `.agent_credentials.json`.
File permissions on POSIX systems are set to `0600` (read/write by owner only).

## 2. Server Authentication

All heartbeat and telemetry endpoints verify `X-Agent-ID` and `X-Agent-Secret` credentials against the server's Argon2/Bcrypt hash repository.

## 3. Secret Protection in Logs

Secrets, raw tokens, and credentials are strictly excluded from structured log outputs.
