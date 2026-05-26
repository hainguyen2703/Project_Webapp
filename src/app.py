from __future__ import annotations

import os
import secrets

from flask import Flask, abort, jsonify, redirect, render_template, request, session, url_for
from src.services.discovery_service import fetch_items

app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-insecure-key-change-in-prod")

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}
FAVOURITES_STORE: dict[str, list[dict]] = {}


@app.route("/")
def home() -> str:
    selected_source = "arxiv"
    query = request.args.get("query", "")
    context = {"query": query}
    result = None

    if request.args.get("fetch"):
        result = fetch_items(selected_source, query=query or None)
        if result["status"] == "success":
            LATEST_RESULTS["arxiv"] = result["items"]
        else:
            LATEST_RESULTS["arxiv"] = []

    return render_template("home.html", result=result, **context)


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
