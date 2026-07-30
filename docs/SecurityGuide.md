# Security Hardening Guide

## Security Headers

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`

## Rate Limiting

Configured at 120 requests/minute per IP in `app/middlewares/rate_limit.py`.
