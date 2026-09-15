# Security Policy

## Supported Versions

The following versions of **AgriSmart AI** are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 2.5.x   | :white_check_mark: |
| 2.0.x   | :x:                |
| < 2.0   | :x:                |

## Reporting a Vulnerability

We take the security of **AgriSmart AI** seriously. If you discover a security vulnerability, please do NOT create a public issue on GitHub. Instead, follow these responsible disclosure steps:

1. **Email:** Send details to the maintainers at `agrismart.security@gmail.com`.
2. **Details to Include:**
   - Detailed description of the vulnerability and affected components (FastAPI backend, ONNX model engine, SQLite database, or frontend).
   - Step-by-step reproduction instructions or proof-of-concept script.
   - Any potential remediation steps or suggested patches.
3. **Response Timeline:**
   - **Initial Acknowledgement:** Within 24–48 hours.
   - **Triage & Status Update:** Within 3 business days.
   - **Fix & Advisory Release:** Coordinated disclosure after release of patch.

## Security Best Practices for Deployment

- **API Keys:** Never commit API keys (NVIDIA NIM, DeepSeek, OpenWeatherMap, Gemini) to git. Store keys securely using environment variables or the in-app BYOK settings drawer which stores credentials locally in SQLite.
- **Input Validation:** Image uploads to `/predict` are validated for MIME type, byte integrity, and dimensions.
- **CORS:** Restrict CORS allowed origins in production within `app/app.py`.
- **Database:** SQLite queries utilize parameterized prepared statements through `aiosqlite` to eliminate SQL injection risks.
