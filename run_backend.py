#!/usr/bin/env python3
"""
Backend runner script for AI Customer Support Agent
Run: python run_backend.py
"""

import os
import sys
import subprocess

def main():
    """Run FastAPI backend"""
    
    # Check if we're in the right directory
    if not os.path.exists('backend_main.py'):
        print("❌ Error: backend_main.py not found!")
        print("Make sure you're in the project root directory")
        sys.exit(1)
    
    # Check environment
    print("🚀 Starting AI Customer Support Agent Backend...")
    print("=" * 60)
    
    # Check for .env file
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("Creating .env from .env.example...")
        if os.path.exists('.env.example'):
            with open('.env.example', 'r') as f:
                env_content = f.read()
            with open('.env', 'w') as f:
                f.write(env_content)
            print("✅ .env file created. Please update it with your Gemini API key")
    
    # Create required directories
    directories = ['./uploads', './vectorstore', './logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created {directory} directory")
    
    print("\n📊 Database Configuration:")
    print("   Database: SQLite (customer_support.db)")
    print("   Location: ./customer_support.db")
    
    print("\n🔐 Admin Account:")
    print("   Username: admin")
    print("   Password: admin")
    print("   (Change this immediately in production!)")
    
    print("\n" + "=" * 60)
    print("🌐 Starting FastAPI Server...")
    print("Backend URL: http://localhost:8000")
    print("API Docs: http://localhost:8000/docs")
    print("=" * 60 + "\n")
    
    # Run uvicorn
    try:
        subprocess.run(
            [sys.executable, '-m', 'uvicorn', 'backend_main:app', '--reload', '--host', '0.0.0.0', '--port', '8000'],
            cwd=os.getcwd()
        )
    except KeyboardInterrupt:
        print("\n\n👋 Backend stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
