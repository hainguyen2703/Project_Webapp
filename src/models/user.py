from __future__ import annotations

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class UserAccount(db.Model):
    __tablename__ = "user_account"
    __allow_unmapped__ = True

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.String(16), nullable=False, default="pending")
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    verified_at = db.Column(db.DateTime, nullable=True)
    consent_at = db.Column(db.DateTime, nullable=False)

    verification_token = db.relationship(
        "VerificationToken", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    email_notifications = db.relationship(
        "EmailNotification", back_populates="user"
    )

    __table_args__ = (
        db.Index("ix_user_account_email", "email"),
        db.Index("ix_user_account_status_created", "status", "created_at"),
    )


class VerificationToken(db.Model):
    __tablename__ = "verification_token"
    __allow_unmapped__ = True

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user_account.id", ondelete="CASCADE"), nullable=False
    )
    token_value = db.Column(db.String(64), unique=True, nullable=False, index=True)
    created_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    resend_count = db.Column(db.Integer, nullable=False, default=0)

    user = db.relationship("UserAccount", back_populates="verification_token")

    __table_args__ = (db.Index("ix_verification_token_user_id", "user_id"),)


class EmailNotification(db.Model):
    __tablename__ = "email_notification"
    __allow_unmapped__ = True

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("user_account.id", ondelete="SET NULL"), nullable=True
    )
    recipient_email = db.Column(db.String(254), nullable=False)
    message_type = db.Column(db.String(32), nullable=False)
    sent_at = db.Column(
        db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    delivery_status = db.Column(db.String(16), nullable=False, default="sent")

    user = db.relationship("UserAccount", back_populates="email_notifications")

