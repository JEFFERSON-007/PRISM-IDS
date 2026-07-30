# Threat Model & Risk Analysis

## STRIDE Threat Categories Analyzed

1. **Spoofing**: Agent HMAC signatures and JWT token verification prevent rogue node spoofing.
2. **Tampering**: All telemetry transfers use TLS HTTPS/WSS channels.
3. **Repudiation**: Append-only Audit Logs record analyst status updates and agent actions.
4. **Information Disclosure**: Passwords hashed with bcrypt; JWT secret stored in environment variables.
5. **Denial of Service**: Token-bucket IP rate-limiting middleware (`RateLimitMiddleware`).
6. **Elevation of Privilege**: Strict Role-Based Access Control (RBAC).
