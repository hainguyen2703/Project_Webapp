# Quickstart: User Email Registration

**Feature**: 002-user-email-registration  
**Phase**: 1 — Design  
**Date**: 2026-05-14

## Prerequisites

- Python 3.11+
- Existing Paper Discovery webapp running (see `specs/001-paper-discovery-site/quickstart.md`)
- SMTP credentials for sending email (Gmail SMTP or any provider)

---

## 1. Install New Dependencies

```bash
pip install Flask-SQLAlchemy>=3.0 Flask-Mail>=0.9.1
```

Update `requirements.txt`:

```
Flask>=2.0
requests>=2.28
beautifulsoup4>=4.12
pytest>=8.0
Flask-SQLAlchemy>=3.0
Flask-Mail>=0.9.1
```

---

## 2. Set Environment Variables

Create or update a `.env` file (never commit to version control):

```env
# Flask
SECRET_KEY=<random-cryptographic-string>   # Required for signed session cookies

# Database (SQLite for dev)
DATABASE_URL=sqlite:///app.db

# Mail (SMTP — example using Gmail SMTP)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-app-email@gmail.com
MAIL_PASSWORD=your-app-password-or-app-specific-token
MAIL_DEFAULT_SENDER=your-app-email@gmail.com
```

> **Note**: For local testing without a real SMTP server, set `MAIL_SUPPRESS_SEND=true` to suppress sends and print to the console.

---

## 3. Run Database Migrations

After adding the new models, initialise the database schema:

```bash
flask db init       # Only needed once (if using Flask-Migrate)
flask db migrate -m "add user registration tables"
flask db upgrade
```

Or, for development without migrations:

```python
# In a Python shell or startup script
from src.app import app, db
with app.app_context():
    db.create_all()
```

---

## 4. Start the Application

```bash
flask run
# or
python -m src.app
```

---

## 5. Verify the Registration Flow

1. Navigate to `http://localhost:8000/register`
2. Enter a `@gmail.com` address, a password (≥8 chars, ≥1 letter, ≥1 digit), and tick the Privacy Policy checkbox.
3. Submit. You should be redirected to `/check-email`.
4. Check your inbox (or console if `MAIL_SUPPRESS_SEND=true`) for the verification email.
5. Click the verification link (`/verify/<token>`). You should see a "Your email has been verified!" confirmation.

---

## 6. Run the Tests

```bash
pytest tests/
```

Key test areas:
- `tests/unit/test_models.py` — UserAccount and VerificationToken model validation
- `tests/unit/test_registration_service.py` — Gmail domain check, password validation, duplicate detection
- `tests/integration/test_registration_flow.py` — End-to-end: register → check-email → verify

---

## Common Issues

| Problem | Likely Cause | Fix |
|---|---|---|
| `RuntimeError: The application's secret key is not set` | `SECRET_KEY` not configured | Set `SECRET_KEY` in `.env` |
| `smtplib.SMTPAuthenticationError` | Wrong SMTP credentials | Check `MAIL_USERNAME` / `MAIL_PASSWORD`; use App Password for Gmail |
| `IntegrityError: UNIQUE constraint failed: user_account.email` | Duplicate email registration attempted | Expected — surfaced as field error to user |
| Verification link returns 404 | Token expired or already used | Check `VerificationToken.expires_at`; use resend flow |
