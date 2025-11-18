#!/usr/bin/env python3
import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("INTELLIGENT MEETING - Minimalist Edition")
    print("=" * 60)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("Error: Python 3.7 or higher is required")
        sys.exit(1)
    
    print("Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", "requirements.txt"])
        print("Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("Warning: Some dependencies may not be installed")
    
    # Download NLTK data
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        print("NLTK data downloaded")
    except:
        pass
    
    print("\nStarting application...")
    print("Access: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        from app import app, socketio
        socketio.run(app, debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\nApplication stopped")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
