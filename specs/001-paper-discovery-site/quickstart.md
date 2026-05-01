# Quickstart: Paper Discovery Website

## Prerequisites
- Python 3.11 installed
- A terminal or PowerShell session
- Optional: `virtualenv` or built-in `venv`

## Setup
1. Open a terminal in the repository root.
2. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Run the Website
1. Start the application:
   ```powershell
   python src/app.py
   ```
2. Open a browser and visit:
   ```text
   http://localhost:8000
   ```
3. Browse the returned papers or articles.

## Verify the Primary Flow
- Website should display a list of items with title, author, date, summary, and source label.
- Clicking an item should reveal or expand additional details.
- If the source is unavailable, the UI should show a readable error message and a retry option.

## Development Notes
- Primary language: Python.
- Optional future components may include C/C++ modules for high-performance parsing or source adapters.
- Java is accepted at low priority only if the project shifts toward an enterprise backend later.
