from __future__ import annotations

import os
from datetime import datetime, timezone

from flask import Flask, abort, flash, jsonify, redirect, render_template, request, session, url_for
from flask_mail import Mail

from src.models.user import db
from src.services.discovery_service import fetch_items
from src.services.login_service import login_user
from src.services.registration_service import (
    register_user,
    resend_verification,
    send_verification_email,
    validate_registration_input,
    verify_account,
)

app = Flask(__name__, template_folder="templates", static_folder="static")

# ── Configuration ─────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

app.config["MAIL_SERVER"] = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
app.config["MAIL_PORT"] = int(os.environ.get("MAIL_PORT", 587))
app.config["MAIL_USE_TLS"] = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
app.config["MAIL_USERNAME"] = os.environ.get("MAIL_USERNAME", "")
app.config["MAIL_PASSWORD"] = os.environ.get("MAIL_PASSWORD", "")
app.config["MAIL_DEFAULT_SENDER"] = os.environ.get("MAIL_DEFAULT_SENDER", "")
app.config["MAIL_SUPPRESS_SEND"] = os.environ.get("MAIL_SUPPRESS_SEND", "false").lower() == "true"

# ── Extensions ─────────────────────────────────────────────────────────────────
db.init_app(app)
mail = Mail(app)

with app.app_context():
    db.create_all()

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}


@app.route("/")
def home() -> str:
    selected_source = "arxiv"
    query = request.args.get("query", "")
    context = {"selected_source": selected_source, "query": query}
    result = None

    if request.args.get("fetch"):
        result = fetch_items(selected_source, query=query or None)
        if result["status"] == "success":
            LATEST_RESULTS[selected_source] = result["items"]
        else:
            LATEST_RESULTS[selected_source] = []

    return render_template("home.html", result=result, logged_in="user_id" in session, **context)


@app.route("/api/listings")
def api_listings():
    source = "arxiv"
    query = request.args.get("query")
    result = fetch_items(source, query=query)
    if result["status"] == "error":
        return jsonify(result), 503
    return jsonify(result)


@app.route("/detail/<path:item_id>")
def item_detail(item_id: str) -> str:
    source = "arxiv"
    items = LATEST_RESULTS.get(source, [])
    item = next((item for item in items if item.get("id") == item_id), None)
    if item is None:
        abort(404)

    return render_template("detail.html", item=item, source=source, logged_in="user_id" in session)


# ── Registration routes ────────────────────────────────────────────────────────

def _mask_email(email: str) -> str:
    local, domain = email.split("@", 1)
    return local[0] + "***@" + domain


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if "user_id" in session:
            return redirect(url_for("home"))
        return render_template("register.html", errors={}, form_values={}, logged_in=False)

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    consent = request.form.get("consent", "")

    errors = validate_registration_input(email, password, consent)
    if errors:
        return render_template("register.html", errors=errors, form_values={"email": email}, logged_in=False), 400

    result, user, token = register_user(email, password, datetime.now(timezone.utc))
    if result == "duplicate":
        errors["email"] = "This email is already registered. Please sign in."
        return render_template("register.html", errors=errors, form_values={"email": email}, logged_in=False), 400

    send_verification_email(user, token, mail)

    session["registration_id"] = user.id
    session["masked_email"] = _mask_email(user.email)
    session["next_resend_allowed_at"] = None
    return redirect(url_for("check_email"))


@app.route("/check-email")
def check_email():
    if "registration_id" not in session:
        return redirect(url_for("register"))
    return render_template(
        "check_email.html",
        masked_email=session.get("masked_email", ""),
        next_resend_allowed_at=session.get("next_resend_allowed_at"),
        resend_message=request.args.get("msg"),
        logged_in="user_id" in session,
    )


@app.route("/resend-verification", methods=["POST"])
def resend_verification_route():
    if "registration_id" not in session:
        return redirect(url_for("register"))

    result, next_allowed = resend_verification(session["registration_id"], mail)

    if result == "sent":
        session["next_resend_allowed_at"] = next_allowed.isoformat() if next_allowed else None
        return redirect(url_for("check_email", msg="sent"))
    if result == "cooldown":
        session["next_resend_allowed_at"] = next_allowed.isoformat() if next_allowed else None
        return redirect(url_for("check_email", msg="cooldown"))
    if result == "limit_reached":
        return redirect(url_for("check_email", msg="limit_reached"))
    # already_active
    session.pop("registration_id", None)
    flash("Your account is already verified.")
    return redirect(url_for("register"))


@app.route("/verify/<token>")
def verify(token: str):
    result = verify_account(token)
    return render_template("verify_result.html", result=result, logged_in="user_id" in session)


# ── Auth routes ───────────────────────────────────────────────────────────────

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))
    if request.method == "GET":
        return render_template("login.html", error=None, form_email="", logged_in=False)
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    user_id, error = login_user(email, password)
    if user_id is not None:
        session["user_id"] = user_id
        return redirect(url_for("home"))
    return render_template("login.html", error=error, form_email=email, logged_in=False)


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
