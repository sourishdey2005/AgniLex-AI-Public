#!/usr/bin/env python3
"""
Frontend runner script for AI Customer Support Agent
Run: python run_frontend.py
"""

import os
import sys
import subprocess
import time

def main():
    """Run Streamlit frontend"""
    
    # Check if we're in the right directory
    if not os.path.exists('frontend_app.py'):
        print("❌ Error: frontend_app.py not found!")
        print("Make sure you're in the project root directory")
        sys.exit(1)
    
    print("🚀 Starting AI Customer Support Agent Frontend...")
    print("=" * 60)
    
    # Check if backend is running
    import socket
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    backend_running = sock.connect_ex(('127.0.0.1', 8000)) == 0
    sock.close()
    
    if not backend_running:
        print("⚠️  Warning: Backend is not running on localhost:8000")
        print("Please start the backend first with: python run_backend.py")
        print("\nStarting in 3 seconds anyway...\n")
        time.sleep(3)
    else:
        print("✅ Backend is running on localhost:8000")
    
    print("\n" + "=" * 60)
    print("🌐 Starting Streamlit Frontend...")
    print("Frontend URL: http://localhost:8501")
    print("=" * 60 + "\n")
    
    # Run streamlit
    try:
        subprocess.run(
            [sys.executable, '-m', 'streamlit', 'run', 'frontend_app.py', '--logger.level=info'],
            cwd=os.getcwd()
        )
    except KeyboardInterrupt:
        print("\n\n👋 Frontend stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
