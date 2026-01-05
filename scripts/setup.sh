#!/bin/bash

set -e

echo "🚀 Starting MyBudget application..."
echo ""

# Check if the API is already running
if lsof -i :8000 > /dev/null 2>&1; then
    echo "⚠️  API is already running on port 8000"
    echo ""
    read -p "Continue with bootstrapping (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "📡 Starting API server on http://127.0.0.1:8000..."
    cd "$(dirname "$0")/.."
    python -m uvicorn main:app --host 127.0.0.1 --port 8000 > /tmp/mybudget_api.log 2>&1 &
    SERVER_PID=$!
    echo "   Server PID: $SERVER_PID"
    echo ""
    
    # Wait for server to start
    echo "⏳ Waiting for API to start..."
    sleep 3
    
    # Check if server started successfully
    if ! lsof -i :8000 > /dev/null 2>&1; then
        echo "❌ Failed to start API server"
        echo "Check logs: tail /tmp/mybudget_api.log"
        exit 1
    fi
    echo "✅ API server started successfully"
    echo ""
fi

# Load bootstrap data
echo "📦 Loading bootstrap data..."
cd "$(dirname "$0")/.."
python scripts/bootstrap.py

echo ""
echo "🎉 All done!"
echo ""
echo "📚 Next steps:"
echo "   1. Explore the API: http://localhost:8000/docs"
echo "   2. View ReDoc: http://localhost:8000/redoc"
echo "   3. Run tests: python -m pytest tests/ -v"
echo ""

