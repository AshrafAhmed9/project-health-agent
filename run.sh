#!/bin/bash
set -e

# Project Health Agent Launcher
echo "🏥 Zycus Project Health Reporting Agent launcher"
echo "================================================="

# Create venv if not exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate and install dependencies
source .venv/bin/activate
echo "📥 Installing/Verifying dependencies..."
pip install -q -r requirements.txt

# Run the complete pipeline
echo "🚀 Executing full reporting pipeline..."
python -m src.main full-run

echo ""
echo "✨ Execution complete! Review the outputs folder."
