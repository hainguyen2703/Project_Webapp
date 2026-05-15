import pytest

from src.models.article import PaperArticle


def test_paper_article_to_dict_and_validate():
    article = PaperArticle(
        id="test-1",
        source="arxiv",
        title="Sample Title",
        authors=["Jane Doe"],
        summary="A brief summary.",
        url="https://arxiv.org/abs/1234.5678",
        published_at="2026-05-01T12:00:00+00:00",
        source_label="arXiv",
        fetched_at="2026-05-01T12:10:00+00:00",
    )

    data = article.to_dict()

    assert data["id"] == "test-1"
    assert data["source"] == "arxiv"
    assert data["url"] == "https://arxiv.org/abs/1234.5678"
    assert PaperArticle.validate(article) is True


def test_paper_article_validate_rejects_invalid_url():
    article = PaperArticle(
        id="test-2",
        source="medium",
        title="Sample Title",
        authors=["Jane Doe"],
        summary="A brief summary.",
        url="not-a-url",
        published_at="2026-05-01T12:00:00+00:00",
        source_label="Medium",
        fetched_at="2026-05-01T12:10:00+00:00",
    )

    assert PaperArticle.validate(article) is False


# ── UserAccount & VerificationToken model tests ────────────────────────────────

from datetime import datetime, timedelta, timezone

import pytest

from src.app import app
from src.models.user import UserAccount, VerificationToken, db as _db
from werkzeug.security import check_password_hash, generate_password_hash


@pytest.fixture()
def test_app():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


def test_user_account_password_is_hashed(test_app):
    with test_app.app_context():
        user = UserAccount(
            email="test@gmail.com",
            password_hash=generate_password_hash("Password1"),
            status="pending",
            created_at=datetime.now(timezone.utc),
            consent_at=datetime.now(timezone.utc),
        )
        _db.session.add(user)
        _db.session.commit()
        assert user.password_hash != "Password1"
        assert check_password_hash(user.password_hash, "Password1")


def test_user_account_status_transitions(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        user = UserAccount(
            email="status@gmail.com",
            password_hash=generate_password_hash("Password1"),
            status="pending",
            created_at=now,
            consent_at=now,
        )
        _db.session.add(user)
        _db.session.commit()
        assert user.status == "pending"
        user.status = "active"
        user.verified_at = now
        _db.session.commit()
        assert user.status == "active"
        assert user.verified_at is not None


def test_verification_token_resend_count_starts_at_zero(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        user = UserAccount(
            email="token@gmail.com",
            password_hash=generate_password_hash("Password1"),
            status="pending",
            created_at=now,
            consent_at=now,
        )
        _db.session.add(user)
        _db.session.flush()
        token = VerificationToken(
            user_id=user.id,
            token_value="abc123",
            created_at=now,
            expires_at=now + timedelta(hours=24),
            resend_count=0,
        )
        _db.session.add(token)
        _db.session.commit()
        assert token.resend_count == 0


def test_verification_token_cascade_delete(test_app):
    with test_app.app_context():
        now = datetime.now(timezone.utc)
        user = UserAccount(
            email="cascade@gmail.com",
            password_hash=generate_password_hash("Password1"),
            status="pending",
            created_at=now,
            consent_at=now,
        )
        _db.session.add(user)
        _db.session.flush()
        token = VerificationToken(
            user_id=user.id,
            token_value="cascade_token",
            created_at=now,
            expires_at=now + timedelta(hours=24),
        )
        _db.session.add(token)
        _db.session.commit()

        _db.session.delete(user)
        _db.session.commit()
        assert VerificationToken.query.filter_by(token_value="cascade_token").first() is None

