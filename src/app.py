from __future__ import annotations

import os
import secrets

from flask_login import LoginManager, current_user, login_user, logout_user
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from src.models.auth_user import AuthUser
from src.services.auth_service import authenticate_user, issue_session_expiry, session_is_expired
from src.services.db import bump_session_version, get_user_by_id, init_db
from src.services.discovery_service import fetch_items
from src.services.registration_service import generate_submission_token, register_user

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")
app.config.setdefault("REGISTRATION_DB_PATH", None)
app.config.setdefault("AUTH_DB_PATH", None)

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}
FAVOURITES_STORE: dict[str, list[dict]] = {}

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
    source = request.args.get("source", "arxiv")
    items = LATEST_RESULTS.get(source, [])
    item = next((item for item in items if item.get("id") == item_id), None)
    
    # Fallback to favourites if not in latest results
    if item is None:
        user_id = session.get("user_id", "")
        item = next((i for i in FAVOURITES_STORE.get(user_id, []) if i.get("id") == item_id), None)
    
    if item is None:
        abort(404)
    
    # Check if paper is favourited
    user_id = session.get("user_id", "")
    is_favourite = any(f.get("id") == item_id for f in FAVOURITES_STORE.get(user_id, []))

    return render_template("detail.html", item=item, source=source, is_favourite=is_favourite)


@app.route("/favourite/toggle", methods=["POST"])
def favourite_toggle():
    item_id = request.form.get("item_id")
    if not item_id:
        return redirect(url_for("home"))
    
    # Ensure user has a session ID
    if "user_id" not in session:
        session["user_id"] = secrets.token_urlsafe(32)
    
    user_id = session["user_id"]
    
    # Initialize user's favourites list if needed
    if user_id not in FAVOURITES_STORE:
        FAVOURITES_STORE[user_id] = []
    
    # Check if already favourited
    favourites = FAVOURITES_STORE[user_id]
    existing_index = next((i for i, f in enumerate(favourites) if f.get("id") == item_id), None)
    
    if existing_index is not None:
        # Remove from favourites
        favourites.pop(existing_index)
    else:
        # Add to favourites - find paper in latest results
        paper = next((p for p in LATEST_RESULTS.get("arxiv", []) if p.get("id") == item_id), None)
        if paper:
            # Prepend to maintain reverse chronological order
            favourites.insert(0, paper)
    
    return redirect(url_for("item_detail", item_id=item_id))


@app.route("/favourites")
def favourites_page():
    # Ensure user has a session ID
    if "user_id" not in session:
        session["user_id"] = secrets.token_urlsafe(32)
    
    user_id = session["user_id"]
    favourites = FAVOURITES_STORE.get(user_id, [])
    
    return render_template("favourites.html", favourites=favourites)


@app.route("/favourite/remove", methods=["POST"])
def favourite_remove():
    item_id = request.form.get("item_id")
    
    if item_id and "user_id" in session:
        user_id = session["user_id"]
        if user_id in FAVOURITES_STORE:
            FAVOURITES_STORE[user_id] = [
                f for f in FAVOURITES_STORE[user_id] if f.get("id") != item_id
            ]
    
    return redirect(url_for("favourites_page"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
