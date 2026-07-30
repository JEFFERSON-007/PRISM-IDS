# User Authentication & Security Architecture

## JWT Authentication Flow

PRISM IDS utilizes signed JSON Web Tokens (JWT) for stateless HTTP request authentication.

### Token Types

1. **Access Token**: Short-lived token (default: 30 minutes) containing subject username, assigned role, and permissions list.
2. **Refresh Token**: Long-lived token (default: 7 days) used to request new access tokens without requiring credentials re-entry.

---

## Account Lockout Policy

To mitigate brute-force attacks:
- 5 consecutive failed login attempts trigger account lockout.
- Locked accounts remain suspended for 15 minutes.
- Successful login resets the failed attempts counter to 0.

---

## REST Endpoints

- `POST /api/v1/auth/login`: Accepts `username` and `password`, returns access & refresh tokens.
- `POST /api/v1/auth/refresh`: Accepts `refresh_token`, returns fresh token pair.
- `POST /api/v1/auth/logout`: Invalidates session context and logs audit entry.
- `POST /api/v1/auth/change-password`: Changes current user password.
