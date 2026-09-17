"""
Main Entry Point for Chongpenyang Barista AI Hybrid RAG.
Starts the unified Flask application serving:
- Web Simulator & Diagnostics Inspector at http://localhost:5000/
- LINE Bot Messaging API Webhook at http://localhost:5000/callback
"""
import sys

# Ensure UTF-8 console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.interfaces.webhook import run_server

if __name__ == "__main__":
    run_server()
