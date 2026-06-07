from __future__ import annotations

import os
import secrets
from typing import Any

from flask_login import LoginManager, current_user, login_user, logout_user
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from src.clients.arxiv_client import extract_arxiv_id
from src.models.auth_user import AuthUser
from src.services.auth_service import authenticate_user, issue_session_expiry, session_is_expired
from src.services.db import (
    add_favourite,
    bump_session_version,
    favourite_exists,
    get_favourite,
    get_user_by_id,
    init_db,
    list_favourites,
    remove_favourite,
)
from src.services.discovery_service import fetch_items
from src.services.registration_service import generate_submission_token, register_user

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")
app.config.setdefault("REGISTRATION_DB_PATH", None)
app.config.setdefault("AUTH_DB_PATH", None)

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}

login_manager = LoginManager(app)

init_db(app.config.get("AUTH_DB_PATH") or app.config.get("REGISTRATION_DB_PATH"))


def _registration_db_path() -> str | None:
    return app.config.get("REGISTRATION_DB_PATH")


def _auth_db_path() -> str | None:
    return app.config.get("AUTH_DB_PATH") or app.config.get("REGISTRATION_DB_PATH")


def _ensure_registration_session_key() -> str:
    if "registration_session_key" not in session:
        session["registration_session_key"] = secrets.token_urlsafe(24)
    return session["registration_session_key"]


def _normalize_item_id(raw_id: str) -> str:
    normalized = extract_arxiv_id(raw_id)
    if normalized:
        return normalized
    return raw_id


def _current_user_id() -> int | None:
    if not current_user.is_authenticated:
        return None
    user_id = current_user.get_id()
    if not user_id:
        return None
    return int(user_id)


def _canonical_source_and_id(source: str, item_id: str) -> tuple[str, str]:
    canonical_source = (source or "arxiv").strip().lower() or "arxiv"
    return canonical_source, _normalize_item_id(item_id)


def _find_paper_in_latest_results(source: str, external_paper_id: str) -> dict[str, Any] | None:
    for paper in LATEST_RESULTS.get(source, []):
        if _normalize_item_id(str(paper.get("id", ""))) != external_paper_id:
            continue
        hydrated = dict(paper)
        hydrated["id"] = external_paper_id
        hydrated["source"] = source
        return hydrated
    return None


def _refresh_expired_auth_session() -> None:
    if not current_user.is_authenticated:
        return
    expires_at = session.get("auth_expires_at")
    if session_is_expired(expires_at):
        session["auth_expires_at"] = issue_session_expiry()


@app.before_request
def refresh_auth_session_before_request() -> None:
    _refresh_expired_auth_session()


@login_manager.user_loader
def load_user(user_id: str) -> AuthUser | None:
    if not user_id:
        return None
    row = get_user_by_id(user_id=int(user_id), db_path=_auth_db_path())
    if row is None:
        return None

    session_version = int(row["session_version"])
    session_auth_version = session.get("auth_version")
    if session_auth_version is not None and int(session_auth_version) != session_version:
        return None

    return AuthUser(user_id=int(row["id"]), email=str(row["email"]), session_version=session_version)


@app.route("/")
def home() -> str:
    selected_source = "arxiv"
    query = request.args.get("query", "")
    registered = request.args.get("registered") == "1"
    logged_in = request.args.get("logged_in") == "1"
    logged_out = request.args.get("logged_out") == "1"
    context = {
        "query": query,
        "registered": registered,
        "logged_in": logged_in,
        "logged_out": logged_out,
    }
    result = None

    if request.args.get("fetch"):
        result = fetch_items(selected_source, query=query or None)
        if result["status"] == "success":
            LATEST_RESULTS["arxiv"] = result["items"]
        else:
            LATEST_RESULTS["arxiv"] = []

    return render_template("home.html", result=result, **context)


@app.route("/login")
def login_page() -> str:
    message = None
    if current_user.is_authenticated:
        message = {"kind": "success", "text": "You are already signed in."}

    return render_template("login.html", form_data={"email": ""}, errors={}, message=message)


@app.route("/login", methods=["POST"])
def login_submit():
    if current_user.is_authenticated:
        return render_template(
            "login.html",
            form_data={"email": ""},
            errors={},
            message={"kind": "success", "text": "You are already signed in."},
        )

    email = request.form.get("email", "")
    password = request.form.get("password", "")
    auth_result = authenticate_user(email=email, password=password, db_path=_auth_db_path())

    if auth_result.success:
        login_user(
            AuthUser(
                user_id=int(auth_result.user_id or 0),
                email=auth_result.email,
                session_version=auth_result.session_version,
            )
        )
        session["auth_version"] = auth_result.session_version
        session["auth_expires_at"] = issue_session_expiry()
        return redirect(url_for("home", logged_in=1))

    status_code = 429 if auth_result.code == "throttled" else 200
    return (
        render_template(
            "login.html",
            form_data={"email": email},
            errors=auth_result.errors,
            message=None,
        ),
        status_code,
    )


@app.route("/logout", methods=["POST"])
def logout_submit():
    if not current_user.is_authenticated:
        abort(403)

    _refresh_expired_auth_session()
    user_id = int(current_user.get_id())
    bump_session_version(user_id=user_id, db_path=_auth_db_path())
    logout_user()
    session.pop("auth_version", None)
    session.pop("auth_expires_at", None)
    return redirect(url_for("home", logged_out=1))


@app.route("/register")
def register_page() -> str:
    _ensure_registration_session_key()
    return render_template(
        "register.html",
        form_data={"email": ""},
        errors={},
        submission_token=generate_submission_token(),
    )


@app.route("/register", methods=["POST"])
def register_submit():
    session_key = _ensure_registration_session_key()
    email = request.form.get("email", "")
    password = request.form.get("password", "")
    submission_token = request.form.get("submission_token", "")

    result = register_user(
        email=email,
        password=password,
        session_key=session_key,
        submission_token=submission_token,
        db_path=_registration_db_path(),
    )

    if result.success:
        return redirect(url_for("home", registered=1))

    status_code = 409 if result.code == "duplicate_submission" else 200
    return (
        render_template(
            "register.html",
            form_data={"email": email},
            errors=result.errors,
            submission_token=generate_submission_token(),
        ),
        status_code,
    )


@app.route("/api/listings")
def api_listings():
    source = request.args.get("source", "")
    query = request.args.get("query")
    if not source:
        return jsonify({"source": "", "status": "error", "items": [], "error_message": "Missing source parameter.", "fetched_at": None}), 400
    result = fetch_items(source, query=query)
    if result["status"] == "error":
        return jsonify(result), 503
    return jsonify(result)


@app.route("/detail/<path:item_id>")
def item_detail(item_id: str) -> str:
    source, normalized_item_id = _canonical_source_and_id(
        request.args.get("source", "arxiv"),
        item_id,
    )
    items = LATEST_RESULTS.get(source, [])
    item = next((item for item in items if _normalize_item_id(str(item.get("id", ""))) == normalized_item_id), None)

    # Fallback to favourites if not in latest results
    user_id = _current_user_id()
    if item is None and user_id is not None:
        item = get_favourite(
            user_id=user_id,
            source=source,
            external_paper_id=normalized_item_id,
            db_path=_auth_db_path(),
        )

    if item is None:
        abort(404)

    item = dict(item)
    item["id"] = normalized_item_id
    item["source"] = source

    # Check if paper is favourited
    is_favourite = False
    if user_id is not None:
        is_favourite = favourite_exists(
            user_id=user_id,
            source=source,
            external_paper_id=normalized_item_id,
            db_path=_auth_db_path(),
        )

    return render_template("detail.html", item=item, source=source, is_favourite=is_favourite)


@app.route("/favourite/toggle", methods=["POST"])
def favourite_toggle():
    if not current_user.is_authenticated:
        abort(404)

    source, item_id = _canonical_source_and_id(
        request.form.get("source", "arxiv"),
        request.form.get("item_id", ""),
    )
    if not item_id:
        return redirect(url_for("home"))

    user_id = _current_user_id()
    if user_id is None:
        abort(404)

    if favourite_exists(
        user_id=user_id,
        source=source,
        external_paper_id=item_id,
        db_path=_auth_db_path(),
    ):
        remove_favourite(
            user_id=user_id,
            source=source,
            external_paper_id=item_id,
            db_path=_auth_db_path(),
        )
    else:
        paper = _find_paper_in_latest_results(source, item_id)
        if paper:
            add_favourite(
                user_id=user_id,
                source=source,
                external_paper_id=item_id,
                paper=paper,
                db_path=_auth_db_path(),
            )

    return redirect(url_for("item_detail", item_id=item_id, source=source))


@app.route("/favourites")
def favourites_page():
    user_id = _current_user_id()
    if user_id is None:
        abort(404)

    favourites = list_favourites(user_id=user_id, db_path=_auth_db_path())

    return render_template("favourites.html", favourites=favourites)


@app.route("/favourite/remove", methods=["POST"])
def favourite_remove():
    if not current_user.is_authenticated:
        abort(404)

    source, item_id = _canonical_source_and_id(
        request.form.get("source", "arxiv"),
        request.form.get("item_id", ""),
    )
    user_id = _current_user_id()

    if user_id is None:
        abort(404)

    if item_id:
        remove_favourite(
            user_id=user_id,
            source=source,
            external_paper_id=item_id,
            db_path=_auth_db_path(),
        )

    return redirect(url_for("favourites_page"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
