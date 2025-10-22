#!/usr/bin/env python3
"""
Simple HTTP server to serve the RiskIQ frontend.
Run this script to serve the webapp locally.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

# Configuration
PORT = 3000
HOST = "localhost"


class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers to allow communication with the backend
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()


def main():
    # Change to the frontend directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)

    # Create server
    with socketserver.TCPServer((HOST, PORT), CustomHTTPRequestHandler) as httpd:
        print(f"🚀 RiskIQ Frontend Server running at http://{HOST}:{PORT}")
        print(f"📁 Serving files from: {frontend_dir}")
        print("🔗 Make sure your backend API is running on http://localhost:8000")
        print("\nPress Ctrl+C to stop the server")

        try:
            # Open browser automatically
            webbrowser.open(f"http://{HOST}:{PORT}")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped")
            sys.exit(0)


if __name__ == "__main__":
    main()
