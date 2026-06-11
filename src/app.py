from __future__ import annotations

import os
import secrets
from typing import Any

from flask_login import LoginManager, current_user, login_user, logout_user
from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from src.clients.arxiv_client import extract_arxiv_id
from src.models.auth_user import AuthUser
from src.services.auth_service import authenticate_user, issue_session_expiry, session_is_expired
import hashlib
from src.services.db import (
    add_favourite,
    bump_session_version,
    favourite_exists,
    get_favourite,
    get_user_by_id,
    init_db,
    is_onboarding_completed,
    list_interest_topics,
    list_user_interest_keys,
    list_favourites,
    load_effective_interest_context,
    reconcile_user_interests,
    remove_favourite,
    set_user_interest_preferences,
    save_paper_snapshot,
    get_paper_snapshot,
    list_paper_snapshots,
    upsert_user_metadata,
    list_user_notifications,
    mark_notification_read,
    mark_notification_dismissed,
    get_related_papers,
    add_paper_notification
)
from src.services.discovery_service import ListingContextKeys, fetch_items
from src.services.registration_service import generate_submission_token, register_user
from src.services.db import get_interest_label
from src.services.advanced_service import (
    calculate_worth_reading_score, score_to_stars, calculate_analytics, compute_and_store_related_papers
)
from src.services.scheduler_service import SchedulerService


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")


# Add Jinja2 filter for md5 hashing
def md5_filter(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

app.jinja_env.filters['md5'] = md5_filter
app.config.setdefault("REGISTRATION_DB_PATH", None)
app.config.setdefault("AUTH_DB_PATH", None)

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}
MIN_INTERESTS = 3
MAX_INTERESTS = 10
MIN_DEFAULT_RESULTS = 50
DISCOVERY_SESSION_QUERY_KEY = "discover_query"

login_manager = LoginManager(app)

init_db(app.config.get("AUTH_DB_PATH") or app.config.get("REGISTRATION_DB_PATH"))
# Initialize scheduler (background jobs)
SchedulerService.initialize()


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


def _discovery_routes() -> set[str]:
    return {"discover_page", "api_listings", "item_detail"}


def _normalize_interest_keys(raw_keys: list[str]) -> list[str]:
    return list(dict.fromkeys([key.strip().lower() for key in raw_keys if key.strip()]))


def _active_interest_key_set() -> set[str]:
    return {topic["key"] for topic in list_interest_topics(active_only=True, db_path=_auth_db_path())}


def _validate_interest_selection(interest_keys: list[str]) -> tuple[bool, str | None]:
    if len(interest_keys) < MIN_INTERESTS:
        return False, f"Please choose at least {MIN_INTERESTS} interests."
    if len(interest_keys) > MAX_INTERESTS:
        return False, f"Please choose no more than {MAX_INTERESTS} interests."
    if len(set(interest_keys)) != len(interest_keys):
        return False, "Duplicate interests are not allowed."
    active_keys = _active_interest_key_set()
    if any(key not in active_keys for key in interest_keys):
        return False, "One or more selected interests are invalid."
    return True, None


def _build_interest_default_query(interest_keys: list[str]) -> str:
    return " OR ".join([f"cat:{key.upper()}" for key in interest_keys])


def _build_active_interest_labels(interest_keys: list[str]) -> list[dict[str, str]]:
    labels: list[dict[str, str]] = []
    for key in interest_keys:
        normalized_key = key.strip().lower()
        if not normalized_key:
            continue
        labels.append({"key": normalized_key, "label": get_interest_label(normalized_key)})
    return labels


def _synchronized_query_value(default_query: str = "") -> str:
    if "query" in request.args:
        current = (request.args.get("query", "") or "").strip()
        if current:
            session[DISCOVERY_SESSION_QUERY_KEY] = current
        else:
            session.pop(DISCOVERY_SESSION_QUERY_KEY, None)
        return current
    return str(session.get(DISCOVERY_SESSION_QUERY_KEY, default_query))


def _discovery_context(*, query: str, registered: bool, logged_in: bool, logged_out: bool, endpoint: str) -> dict[str, Any]:
    return {
        "query": query,
        "registered": registered,
        "logged_in": logged_in,
        "logged_out": logged_out,
        "default_interest_keys": [],
        "active_interest_labels": [],
        "used_default_interest_query": False,
        "backfill_applied": False,
        "show_sparse_guidance": False,
        "search_action": url_for(endpoint),
        "clear_url": url_for(endpoint, query=""),
    }


def _execute_discovery_fetch(*, selected_source: str, query: str, context: dict[str, Any]) -> dict[str, Any] | None:
    if context["search_action"] == url_for("home") and not query:
        return None
    result = None
    if request.args.get("fetch"):
        fetch_query = query or None
        user_id = _current_user_id()
        interest_keys: list[str] = []
        if user_id is not None and not fetch_query and is_onboarding_completed(user_id=user_id, db_path=_auth_db_path()):
            effective_context = load_effective_interest_context(
                user_id=user_id,
                minimum_count=MIN_INTERESTS,
                db_path=_auth_db_path(),
            )
            interest_keys = effective_context["effective_interest_keys"]
            if interest_keys:
                fetch_query = _build_interest_default_query(interest_keys)
                context["default_interest_keys"] = interest_keys
                context["active_interest_labels"] = _build_active_interest_labels(interest_keys)
                context["used_default_interest_query"] = True

        result = fetch_items(
            selected_source,
            query=fetch_query,
            interest_keys=interest_keys,
            minimum_result_count=MIN_DEFAULT_RESULTS,
        )
        context["used_default_interest_query"] = bool(
            result.get(ListingContextKeys.USED_DEFAULT_INTEREST_QUERY, context["used_default_interest_query"])
        )
        context["backfill_applied"] = bool(result.get(ListingContextKeys.BACKFILL_APPLIED, False))
        context["show_sparse_guidance"] = context["backfill_applied"] or result.get("status") == "empty"

        if context["used_default_interest_query"]:
            context["default_interest_keys"] = list(result.get(ListingContextKeys.ACTIVE_INTEREST_KEYS, context["default_interest_keys"]))
            context["active_interest_labels"] = _build_active_interest_labels(context["default_interest_keys"])

        if result["status"] == "success":
            LATEST_RESULTS["arxiv"] = result["items"]
            # Save all fetched papers to snapshots
            new_papers = []
            for paper in result["items"]:
                paper_categories = paper.get("metadata", {}).get("categories", [])
                save_paper_snapshot(
                    paper_id=paper["id"],
                    source=paper.get("source", "arxiv"),
                    title=paper["title"],
                    authors=paper.get("authors", []),
                    summary=paper.get("summary", ""),
                    url=paper.get("url", ""),
                    published_at=paper.get("published_at", ""),
                    primary_category=paper.get("metadata", {}).get("primary_category"),
                    categories=paper_categories,
                    metadata=paper.get("metadata", {})
                )
                new_papers.append(paper)
            # Now compute related papers!
            compute_and_store_related_papers()
            
            # Add notifications for all users about these new papers, avoid duplicates
            if current_user.is_authenticated:
                user_id = _current_user_id()
                user_interests = list_user_interest_keys(user_id=user_id)
                existing_notifications = list_user_notifications(user_id=user_id, only_undismissed=False)
                existing_paper_ids = {n["paper_id"] for n in existing_notifications}
                for paper in new_papers:
                    if paper["id"] in existing_paper_ids:
                        continue
                    paper_cats = paper.get("metadata", {}).get("categories", [])
                    has_matching_interest = any(interest in paper_cats for interest in user_interests)
                    if has_matching_interest:
                        add_paper_notification(
                            user_id=user_id,
                            paper_id=paper["id"],
                            paper_title=paper["title"],
                            paper_url=paper["url"]
                        )
        else:
            LATEST_RESULTS["arxiv"] = []
    return result


def _render_discovery_view(*, template_name: str, endpoint: str, allow_banner_messages: bool) -> str:
    selected_source = "arxiv"
    query = _synchronized_query_value()
    
    # Add to search history if query is not empty
    if query.strip():
        # Initialize search history if it doesn't exist
        if "search_history" not in session:
            session["search_history"] = []
        
        # Remove query if already present to avoid duplicates
        session["search_history"] = [
            q for q in session["search_history"] 
            if q.lower() != query.lower()
        ]
        
        # Add query to front of history
        session["search_history"].insert(0, query)
        
        # Keep only last 10 searches
        session["search_history"] = session["search_history"][:10]
        
        # Mark session modified to save changes
        session.modified = True
    registered = allow_banner_messages and request.args.get("registered") == "1"
    logged_in = allow_banner_messages and request.args.get("logged_in") == "1"
    logged_out = allow_banner_messages and request.args.get("logged_out") == "1"

    # Pagination params
    page = int(request.args.get("page", 1))
    per_page = 10  # bạn có thể đổi 20 → 30 → 50 tùy ý

    context = _discovery_context(
        query=query,
        registered=registered,
        logged_in=logged_in,
        logged_out=logged_out,
        endpoint=endpoint
    )

    result = _execute_discovery_fetch(
        selected_source=selected_source,
        query=query,
        context=context
    )

    # Nếu có kết quả → áp dụng pagination and mark duplicates
    if result and result.get("items"):
        items = result["items"]
        total = len(items)

        # Track seen paper IDs for duplicate detection
        seen_ids = set()
        # Get user favourites if logged in
        user_id = _current_user_id()
        favourites = []
        if user_id:
            favourites = list_favourites(user_id=user_id, db_path=_auth_db_path())
            # Filter to only arxiv favourites
            favourites = [f for f in favourites if f["source"] == "arxiv"]
            favourite_ids = {_normalize_item_id(str(f["id"])) for f in favourites}
        else:
            favourite_ids = set()
        
        # Add duplicate and favourite flags to items
        processed_items = []
        for item in items:
            normalized_id = _normalize_item_id(str(item.get("id", "")))
            is_duplicate = normalized_id in seen_ids
            seen_ids.add(normalized_id)
            item_with_flag = dict(item)
            item_with_flag["is_duplicate"] = is_duplicate
            item_with_flag["is_favourite"] = normalized_id in favourite_ids
            processed_items.append(item_with_flag)

        # Now apply pagination
        start = (page - 1) * per_page
        end = start + per_page
        result["items"] = processed_items[start:end]
        result["page"] = page
        result["per_page"] = per_page
        result["total"] = total
        result["pages"] = (total + per_page - 1) // per_page

    return render_template(template_name, result=result, **context)


def _refresh_expired_auth_session() -> None:
    if not current_user.is_authenticated:
        return
    expires_at = session.get("auth_expires_at")
    if session_is_expired(expires_at):
        session["auth_expires_at"] = issue_session_expiry()


@app.before_request
def refresh_auth_session_before_request() -> None:
    _refresh_expired_auth_session()
    user_id = _current_user_id()
    if user_id is None:
        return

    reconcile_user_interests(user_id=user_id, minimum_count=MIN_INTERESTS, db_path=_auth_db_path())

    endpoint = request.endpoint or ""
    if endpoint in _discovery_routes() and not is_onboarding_completed(user_id=user_id, db_path=_auth_db_path()):
        return redirect(url_for("onboarding_interests_page"))


@app.context_processor
def inject_active_route() -> dict[str, str]:
    endpoint = request.endpoint or ""
    if endpoint == "home":
        active_page = "home"
    elif endpoint == "discover_page":
        active_page = "discover"
    else:
        active_page = ""
    return {"active_page": active_page}


@app.context_processor
def inject_notifications() -> dict[str, Any]:
    user_id = _current_user_id()
    notifications = []
    if user_id:
        notifications = list_user_notifications(user_id=user_id, only_undismissed=True)
    return {"notifications": notifications}


@app.route("/notification/<int:notification_id>/mark-read", methods=["POST"])
def mark_notification_as_read(notification_id: int):
    if not current_user.is_authenticated:
        abort(403)
    mark_notification_read(notification_id=notification_id, db_path=_auth_db_path())
    return redirect(request.referrer or url_for("home"))


@app.route("/notification/<int:notification_id>/dismiss", methods=["POST"])
def dismiss_notification(notification_id: int):
    if not current_user.is_authenticated:
        abort(403)

    mark_notification_dismissed(notification_id=notification_id, db_path=_auth_db_path())

    # Nếu là AJAX → trả JSON, không redirect
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "ok"})

    # Nếu không phải AJAX → fallback redirect
    return redirect(request.referrer or url_for("home"))




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
    return _render_discovery_view(template_name="home.html", endpoint="home", allow_banner_messages=True)


@app.route("/discover")
def discover_page() -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))
    return _render_discovery_view(template_name="discover.html", endpoint="discover_page", allow_banner_messages=False)


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
        user_id = int(auth_result.user_id or 0)
        login_user(
            AuthUser(
                user_id=user_id,
                email=auth_result.email,
                session_version=auth_result.session_version,
            )
        )
        session["auth_version"] = auth_result.session_version
        session["auth_expires_at"] = issue_session_expiry()
        # Update last login time in user metadata
        from datetime import datetime, timezone
        upsert_user_metadata(user_id=user_id, last_login_at=datetime.now(timezone.utc).isoformat())
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
    session.pop(DISCOVERY_SESSION_QUERY_KEY, None)
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


@app.route("/test-notifications", methods=["GET", "POST"])
def test_notifications():
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))
    
    # First, let's add a TEST notification manually so we can see it!
    user_id = _current_user_id()
    add_paper_notification(
        user_id=user_id,
        paper_id="2606.12345v1",
        paper_title="Test Paper: Advanced ML for Everything",
        paper_url="https://arxiv.org/abs/2606.12345v1"
    )
    
    # Also manually run the notification check
    from src.services.scheduler_service import check_new_papers_for_all_users
    check_new_papers_for_all_users()
    
    return redirect(url_for("home"))


@app.route("/analytics", endpoint="analytics_page")
def analytics_page():
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))
    analytics_data = calculate_analytics()
    notifications = list_user_notifications(
        user_id=_current_user_id(),
        only_undismissed=True,
        limit=10
    ) if _current_user_id() else []
    return render_template("analytics.html", analytics=analytics_data, notifications=notifications)


@app.route("/api/listings")
def api_listings():
    source = request.args.get("source", "")
    query = request.args.get("query")
    if not source:
        return jsonify({"source": "", "status": "error", "items": [], "error_message": "Missing source parameter.", "fetched_at": None}), 400
    fetch_query = query
    user_id = _current_user_id()
    interest_keys: list[str] = []
    if user_id is not None and not fetch_query and is_onboarding_completed(user_id=user_id, db_path=_auth_db_path()):
        effective_context = load_effective_interest_context(
            user_id=user_id,
            minimum_count=MIN_INTERESTS,
            db_path=_auth_db_path(),
        )
        interest_keys = effective_context["effective_interest_keys"]
        if interest_keys:
            fetch_query = _build_interest_default_query(interest_keys)

    result = fetch_items(
        source,
        query=fetch_query,
        interest_keys=interest_keys,
        minimum_result_count=MIN_DEFAULT_RESULTS,
    )
    if result["status"] == "error":
        return jsonify(result), 503
    return jsonify(result)


@app.route("/onboarding/interests")
def onboarding_interests_page() -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    user_id = _current_user_id()
    if user_id is None:
        return redirect(url_for("login_page"))

    if is_onboarding_completed(user_id=user_id, db_path=_auth_db_path()):
        return redirect(url_for("home"))

    topics = list_interest_topics(active_only=True, db_path=_auth_db_path())
    selected_keys = list_user_interest_keys(user_id=user_id, active_only=True, db_path=_auth_db_path())
    return render_template(
        "onboarding_interests.html",
        topics=topics,
        selected_keys=selected_keys,
        min_interests=MIN_INTERESTS,
        max_interests=MAX_INTERESTS,
        error_message=None,
    )


@app.route("/onboarding/interests", methods=["POST"])
def onboarding_interests_submit() -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    user_id = _current_user_id()
    if user_id is None:
        return redirect(url_for("login_page"))

    selected = _normalize_interest_keys(request.form.getlist("interest_keys"))
    valid, error = _validate_interest_selection(selected)
    if not valid:
        return render_template(
            "onboarding_interests.html",
            topics=list_interest_topics(active_only=True, db_path=_auth_db_path()),
            selected_keys=selected,
            min_interests=MIN_INTERESTS,
            max_interests=MAX_INTERESTS,
            error_message=error,
        )

    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=selected,
        onboarding_completed=True,
        db_path=_auth_db_path(),
    )
    return redirect(url_for("home"))


@app.route("/interests")
def interests_page() -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    user_id = _current_user_id()
    if user_id is None:
        return redirect(url_for("login_page"))
    if not is_onboarding_completed(user_id=user_id, db_path=_auth_db_path()):
        return redirect(url_for("onboarding_interests_page"))

    return render_template(
        "interests.html",
        topics=list_interest_topics(active_only=True, db_path=_auth_db_path()),
        selected_keys=list_user_interest_keys(user_id=user_id, active_only=True, db_path=_auth_db_path()),
        min_interests=MIN_INTERESTS,
        max_interests=MAX_INTERESTS,
        error_message=None,
    )


@app.route("/interests", methods=["POST"])
def interests_submit() -> str:
    if not current_user.is_authenticated:
        return redirect(url_for("login_page"))

    user_id = _current_user_id()
    if user_id is None:
        return redirect(url_for("login_page"))

    selected = _normalize_interest_keys(request.form.getlist("interest_keys"))
    valid, error = _validate_interest_selection(selected)
    if not valid:
        return render_template(
            "interests.html",
            topics=list_interest_topics(active_only=True, db_path=_auth_db_path()),
            selected_keys=selected,
            min_interests=MIN_INTERESTS,
            max_interests=MAX_INTERESTS,
            error_message=error,
        )

    set_user_interest_preferences(
        user_id=user_id,
        interest_keys=selected,
        onboarding_completed=True,
        db_path=_auth_db_path(),
    )
    return redirect(url_for("interests_page"))


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

    # Fallback to fetching from arXiv directly
    if item is None:
        from src.clients.arxiv_client import fetch_single_paper
        item = fetch_single_paper(normalized_item_id)
        if item:
            # Save it as a snapshot!
            save_paper_snapshot(
                paper_id=item["id"],
                source="arxiv",
                title=item["title"],
                authors=item["authors"],
                summary=item["summary"],
                url=item["url"],
                published_at=item["published_at"],
                primary_category=item["metadata"]["primary_category"],
                categories=item["metadata"]["categories"],
                metadata=item["metadata"]
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
    
    primary_category = item.get("metadata", {}).get("primary_category", "").lower()
    item["primary_category_label"] = get_interest_label(primary_category)        

    # Calculate "worth reading" score
    score = None
    if user_id is not None:
        user_interests = list_user_interest_keys(user_id=user_id, db_path=_auth_db_path())
        paper_cats = item.get("metadata", {}).get("categories", [])
        score = calculate_worth_reading_score(
            item["published_at"],
            paper_cats,
            user_interests,
            primary_category
        )

    # Get related papers and fetch full info
    related_paper_ids = get_related_papers(source_paper_id=normalized_item_id, limit=5)
    # Enrich with actual paper info
    enriched_related = []
    for rel in related_paper_ids:
        try:
            snap = get_paper_snapshot(paper_id=rel["target_paper_id"], source="arxiv")
            if snap:
                enriched_related.append({
                    "id": snap["id"],
                    "title": snap["title"],
                    "url": snap["url"],
                    "similarity": round(rel["similarity_score"], 2)
                })
            else:
                # Try to find in latest results
                found_item = next((i for i in items if _normalize_item_id(str(i.get("id", ""))) == rel["target_paper_id"]), None)
                if found_item:
                    enriched_related.append({
                        "id": found_item["id"],
                        "title": found_item["title"],
                        "url": found_item["url"],
                        "similarity": round(rel["similarity_score"], 2)
                    })
        except Exception:
            # Skip this related paper if there's an error
            pass
    
    # If no related papers found, add some recent saved papers as fallbacks
    if len(enriched_related) < 3:
        recent_snapshots = list_paper_snapshots(limit=5)
        for snap in recent_snapshots:
            if snap["id"] != normalized_item_id:  # Don't include the current paper
                # Check if we already have this paper
                already_added = any(rel["id"] == snap["id"] for rel in enriched_related)
                if not already_added and len(enriched_related) < 5:
                    enriched_related.append({
                        "id": snap["id"],
                        "title": snap["title"],
                        "url": snap["url"],
                        "similarity": "Recent"
                    })

    return render_template(
        "detail.html",
        item=item,
        source=source,
        is_favourite=is_favourite,
        score=score,
        score_stars=score_to_stars(score["overall_score"]) if score else 0,
        related_papers=enriched_related
    )


@app.route("/favourite/toggle", methods=["POST"])
def favourite_toggle():
    if not current_user.is_authenticated:
        return jsonify({"error": "Not logged in"}), 401

    source, item_id = _canonical_source_and_id(
        request.form.get("source", "arxiv"),
        request.form.get("item_id", ""),
    )
    if not item_id:
        return jsonify({"error": "No item ID"}), 400

    user_id = _current_user_id()
    if user_id is None:
        return jsonify({"error": "Not logged in"}), 401

    is_favourite = False
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
            is_favourite = True

    return jsonify({"item_id": item_id, "is_favourite": is_favourite})


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
