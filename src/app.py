from __future__ import annotations

from flask import Flask, abort, jsonify, redirect, render_template, request, url_for
from src.services.discovery_service import fetch_items

app = Flask(__name__, template_folder="templates", static_folder="static")

LATEST_RESULTS: dict[str, list[dict]] = {"arxiv": []}


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
    if item is None:
        abort(404)

    return render_template("detail.html", item=item, source=source)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
