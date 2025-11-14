"""Minimal Flask entry point for the Job Search Automation demo."""
from job_search_automation.webapp import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
