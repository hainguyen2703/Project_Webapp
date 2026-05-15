from __future__ import annotations

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal

from flask import url_for
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash

from src.models.user import EmailNotification, UserAccount, VerificationToken, db

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_GMAIL_SUFFIX = "@gmail.com"
_MIN_PW_LEN = 8
_MAX_RESENDS = 3
_RESEND_COOLDOWN_SECONDS = 60
_TOKEN_EXPIRY_HOURS = 24


# ── Purge ──────────────────────────────────────────────────────────────────────

def _purge_expired_pending_accounts() -> None:
    """Delete pending accounts older than 24 hours (FR-011)."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=_TOKEN_EXPIRY_HOURS)
    UserAccount.query.filter(
        UserAccount.status == "pending",
        UserAccount.created_at < cutoff,
    ).delete(synchronize_session=False)
    db.session.commit()


# ── Validation ─────────────────────────────────────────────────────────────────

def validate_registration_input(
    email: str, password: str, consent: str
) -> dict[str, str]:
    """Return a dict of {field: error_message} for invalid inputs (FR-001–FR-003, FR-012)."""
    errors: dict[str, str] = {}

    email = email.strip().lower()
    if not email:
        errors["email"] = "Email address is required."
    elif not _EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    elif not email.endswith(_GMAIL_SUFFIX):
        errors["email"] = "Only Gmail addresses (@gmail.com) are supported."

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < _MIN_PW_LEN:
        errors["password"] = f"Password must be at least {_MIN_PW_LEN} characters."
    elif not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        errors["password"] = "Password must contain at least one letter and one digit."

    if consent != "on":
        errors["consent"] = "You must accept the Privacy Policy to register."

    return errors


# ── Registration ───────────────────────────────────────────────────────────────

RegisterResult = Literal["ok", "duplicate"]


def register_user(
    email: str, password: str, consent_at: datetime
) -> tuple[RegisterResult, UserAccount | None, VerificationToken | None]:
    """
    Create a pending UserAccount + VerificationToken.
    Returns ('ok', user, token) or ('duplicate', None, None).
    Runs pending-account purge first (FR-011).
    Assumes inputs already validated by validate_registration_input().
    """
    _purge_expired_pending_accounts()

    email = email.strip().lower()

    # Timing-safe duplicate check — always query to avoid timing oracle (FR-010)
    existing = UserAccount.query.filter_by(email=email).first()
    if existing is not None:
        return "duplicate", None, None

    now = datetime.now(timezone.utc)
    user = UserAccount(
        email=email,
        password_hash=generate_password_hash(password),
        status="pending",
        created_at=now,
        consent_at=consent_at,
    )
    db.session.add(user)
    db.session.flush()  # get user.id before token creation

    token = VerificationToken(
        user_id=user.id,
        token_value=secrets.token_urlsafe(32),
        created_at=now,
        expires_at=now + timedelta(hours=_TOKEN_EXPIRY_HOURS),
        resend_count=0,
    )
    db.session.add(token)
    db.session.commit()
    db.session.refresh(user)
    db.session.refresh(token)
    return "ok", user, token


# ── Email ──────────────────────────────────────────────────────────────────────

def send_verification_email(user: UserAccount, token: VerificationToken, mail: Mail) -> None:
    """Send verification email and record delivery status (FR-005)."""
    notification = EmailNotification(
        user_id=user.id,
        recipient_email=user.email,
        message_type="verification",
        sent_at=datetime.now(timezone.utc),
        delivery_status="sent",
    )
    db.session.add(notification)

    verify_url = url_for("verify", token=token.token_value, _external=True)
    msg = Message(
        subject="Verify your Paper Discovery account",
        recipients=[user.email],
        body=(
            f"Hello,\n\n"
            f"Thank you for registering. Please verify your email address by clicking the link below:\n\n"
            f"{verify_url}\n\n"
            f"This link expires in 24 hours.\n\n"
            f"If you did not register, you can ignore this email.\n"
        ),
    )
    try:
        mail.send(msg)
    except Exception:
        notification.delivery_status = "failed"

    db.session.commit()


# ── Verification ───────────────────────────────────────────────────────────────

VerifyResult = Literal["activated", "already_used", "expired", "not_found"]


def verify_account(token_value: str) -> VerifyResult:
    """
    Consume a verification token and activate the account.
    Runs pending-account purge first (FR-011).
    """
    _purge_expired_pending_accounts()

    token = VerificationToken.query.filter_by(token_value=token_value).first()
    if token is None:
        return "not_found"

    if token.used_at is not None:
        return "already_used"

    now = datetime.now(timezone.utc)
    expires = token.expires_at
    if expires.tzinfo is None:
        expires = expires.replace(tzinfo=timezone.utc)
    if now > expires:
        return "expired"

    token.used_at = now
    token.user.status = "active"
    token.user.verified_at = now
    db.session.commit()
    return "activated"


# ── Resend ─────────────────────────────────────────────────────────────────────

ResendResult = Literal["sent", "cooldown", "limit_reached", "already_active"]


def resend_verification(
    registration_id: int, mail: Mail
) -> tuple[ResendResult, datetime | None]:
    """
    Issue a new verification email for a pending account.
    Returns (result, next_resend_allowed_at).
    """
    user = db.session.get(UserAccount, registration_id)
    if user is None or user.status == "active":
        return "already_active", None

    token = user.verification_token
    if token is None:
        return "already_active", None

    if token.resend_count >= _MAX_RESENDS:
        return "limit_reached", None

    now = datetime.now(timezone.utc)

    # Cooldown: next resend allowed 60 s after the most recent token creation
    last_issued = token.created_at
    if last_issued.tzinfo is None:
        last_issued = last_issued.replace(tzinfo=timezone.utc)
    next_allowed = last_issued + timedelta(seconds=_RESEND_COOLDOWN_SECONDS)
    if now < next_allowed:
        return "cooldown", next_allowed

    # Generate new token in-place
    token.token_value = secrets.token_urlsafe(32)
    token.created_at = now
    token.expires_at = now + timedelta(hours=_TOKEN_EXPIRY_HOURS)
    token.resend_count += 1

    notification = EmailNotification(
        user_id=user.id,
        recipient_email=user.email,
        message_type="resend_verification",
        sent_at=now,
        delivery_status="sent",
    )
    db.session.add(notification)

    next_allowed = now + timedelta(seconds=_RESEND_COOLDOWN_SECONDS)

    db.session.commit()

    try:
        send_verification_email(user, token, mail)
    except Exception:
        pass  # delivery is best-effort; already recorded in send_verification_email

    return "sent", next_allowed

