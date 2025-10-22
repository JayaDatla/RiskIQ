#!/usr/bin/env python3
"""
Startup script for RiskIQ Web Application
This script starts both the backend API and frontend server.
"""

import subprocess
import sys
import time
import threading
import webbrowser
import os
from pathlib import Path


def start_backend():
    """Start the FastAPI backend server"""
    print("🚀 Starting RiskIQ Backend API...")
    try:
        # Change to project root directory
        project_root = Path(__file__).parent
        os.chdir(project_root)

        # Start uvicorn server
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "backend.api.app:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")
    except KeyboardInterrupt:
        print("🛑 Backend stopped")


def start_frontend():
    """Start the frontend HTTP server"""
    print("🌐 Starting RiskIQ Frontend Server...")
    try:
        # Change to frontend directory
        frontend_dir = Path(__file__).parent / "frontend"
        os.chdir(frontend_dir)

        # Start the frontend server
        subprocess.run([sys.executable, "server.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
    except KeyboardInterrupt:
        print("🛑 Frontend stopped")


def main():
    """Main function to start both servers"""
    print("=" * 60)
    print("🎯 RiskIQ Web Application Startup")
    print("=" * 60)
    print()

    # Check if we're in the right directory
    if not Path("backend/api/app.py").exists():
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected structure: Project_2_RiskIQ/start_webapp.py")
        sys.exit(1)

    if not Path("frontend/index.html").exists():
        print("❌ Error: Frontend files not found")
        print("   Please ensure frontend/ directory exists with index.html")
        sys.exit(1)

    print("✅ Project structure verified")
    print()

    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()

    # Wait a moment for backend to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(3)

    # Start frontend
    try:
        start_frontend()
    except KeyboardInterrupt:
        print("\n👋 Shutting down RiskIQ Web Application...")
        print("   Backend and frontend servers stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
