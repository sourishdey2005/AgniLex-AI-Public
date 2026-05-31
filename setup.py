#!/usr/bin/env python3
"""
Setup initialization script for AI Customer Support Agent
Helps with first-time setup and configuration
"""

import os
import sys
import shutil
from pathlib import Path

def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     🤖 AI Customer Support Agent Setup Wizard 🤖             ║
    ║                                                              ║
    ║         Production-Ready Local AI Platform                  ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor} - Need 3.8+")
        return False

def check_directories():
    """Check and create required directories"""
    directories = [
        'uploads',
        'vectorstore',
        'logs'
    ]
    
    print("\n📁 Checking directories...")
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
            print(f"   ✅ Created {directory}/")
        else:
            print(f"   ✅ Found {directory}/")

def create_env_file():
    """Create .env file if it doesn't exist"""
    print("\n🔐 Setting up environment variables...")
    
    if os.path.exists('.env'):
        print("   ⚠️  .env already exists - skipping")
        return
    
    if not os.path.exists('.env.example'):
        print("   ❌ .env.example not found!")
        return False
    
    # Copy .env.example to .env
    shutil.copy('.env.example', '.env')
    print("   ✅ Created .env file")
    
    # Prompt for OpenAI API key
    print("\n   📌 Required: OpenAI API Key")
    print("      1. Go to https://platform.openai.com/api-keys")
    print("      2. Create or copy your API key")
    
    api_key = input("   Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if api_key:
        with open('.env', 'r') as f:
            content = f.read()
        
        content = content.replace(
            'OPENAI_API_KEY=your-openai-api-key-here',
            f'OPENAI_API_KEY={api_key}'
        )
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("   ✅ OpenAI API key saved")
    else:
        print("   ⚠️  Skipped API key - you'll need to add it to .env later")
    
    # Generate secret key
    import secrets
    secret_key = secrets.token_urlsafe(32)
    
    with open('.env', 'r') as f:
        content = f.read()
    
    content = content.replace(
        'SECRET_KEY=your-secret-key-change-in-production',
        f'SECRET_KEY={secret_key}'
    )
    
    with open('.env', 'w') as f:
        f.write(content)
    
    print("   ✅ Generated SECRET_KEY")
    
    return True

def check_files():
    """Check if all required files exist"""
    print("\n📄 Checking required files...")
    
    required_files = [
        'requirements.txt',
        'backend_models.py',
        'backend_auth.py',
        'backend_rag.py',
        'backend_chat.py',
        'backend_main.py',
        'frontend_app.py',
        'run_backend.py',
        'run_frontend.py',
        '.env.example',
        'README.md'
    ]
    
    missing = []
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            missing.append(file)
    
    if missing:
        print(f"\n❌ Missing {len(missing)} files. Please download all project files.")
        return False
    
    return True

def show_next_steps():
    """Show next steps"""
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    print("\n🚀 Next Steps:")
    print("\n1️⃣  Install Dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2️⃣  Start Backend (Terminal 1):")
    print("   python run_backend.py")
    
    print("\n3️⃣  Start Frontend (Terminal 2):")
    print("   python run_frontend.py")
    
    print("\n4️⃣  Open Browser:")
    print("   http://localhost:8501")
    
    print("\n5️⃣  Login with Admin Account:")
    print("   Username: admin")
    print("   Password: admin")
    
    print("\n📚 Documentation:")
    print("   - Quick Start: See QUICKSTART.md")
    print("   - Full Guide: See README.md")
    print("   - API Docs: http://localhost:8000/docs (after starting backend)")
    
    print("\n⚠️  Security Reminder:")
    print("   Change admin password immediately in Settings!")
    
    print("\n" + "="*60 + "\n")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Setup failed: Python 3.8+ required")
        sys.exit(1)
    
    # Check files
    if not check_files():
        print("\n❌ Setup failed: Missing required files")
        sys.exit(1)
    
    # Create directories
    check_directories()
    
    # Create .env
    try:
        if not create_env_file():
            print("⚠️  Skipped .env creation")
    except Exception as e:
        print(f"⚠️  Error creating .env: {e}")
    
    # Show next steps
    show_next_steps()
    
    print("Ready to launch! 🚀")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
