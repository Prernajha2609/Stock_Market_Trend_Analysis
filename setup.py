"""
Setup script for Stock Market Prediction Project.
"""
import os
import sys
import subprocess
import nltk
from pathlib import Path

def install_requirements():
    """Install required packages."""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Packages installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing packages: {e}")
        return False
    return True

def download_nltk_data():
    """Download required NLTK data."""
    print("📚 Downloading NLTK data...")
    try:
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data downloaded successfully!")
    except Exception as e:
        print(f"❌ Error downloading NLTK data: {e}")
        return False
    return True

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        try:
            with open("env.example", "r") as example_file:
                example_content = example_file.read()
            
            with open(".env", "w") as env_file:
                env_file.write(example_content)
            
            print("✅ .env file created! Please update it with your database credentials.")
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    else:
        print("ℹ️ .env file already exists.")
    return True

def create_directories():
    """Create necessary directories."""
    print("📁 Creating directories...")
    directories = ["logs", "data/raw", "data/processed"]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directories created successfully!")
    return True

def test_imports():
    """Test if all imports work correctly."""
    print("🧪 Testing imports...")
    try:
        import pandas as pd
        import numpy as np
        import yfinance as yf
        import streamlit as st
        import plotly.graph_objects as go
        import sklearn
        import statsmodels
        import nltk
        from nltk.sentiment import SentimentIntensityAnalyzer
        
        print("✅ All imports successful!")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up Stock Market Prediction Project...")
    print("=" * 50)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at package installation.")
        return False
    
    # Download NLTK data
    if not download_nltk_data():
        print("❌ Setup failed at NLTK data download.")
        return False
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation.")
        return False
    
    # Create directories
    if not create_directories():
        print("❌ Setup failed at directory creation.")
        return False
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed at import testing.")
        return False
    
    print("=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your database credentials")
    print("2. Set up PostgreSQL database")
    print("3. Run: python data/stock_data_collector.py --symbol AAPL")
    print("4. Run: python data/news_data_collector.py --symbol AAPL")
    print("5. Run: python data/data_cleaner.py --symbol AAPL")
    print("6. Run: streamlit run dashboard/app.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 