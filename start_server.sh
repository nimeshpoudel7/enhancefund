#!/bin/bash

echo "========================================"
echo "Starting EnhanceFund Server"
echo "with WebSocket Support (Daphne)"
echo "========================================"
echo ""

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "WARNING: Virtual environment not detected!"
    echo "Please activate your virtual environment first."
    echo ""
    read -p "Press enter to continue anyway..."
fi

# Check if daphne is installed
if ! command -v daphne &> /dev/null; then
    echo "ERROR: Daphne is not installed!"
    echo "Please run: pip install daphne==4.1.0"
    echo ""
    exit 1
fi

echo "Starting server on http://localhost:8000"
echo "WebSocket available at ws://localhost:8000/ws/notifications/"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

daphne -b 0.0.0.0 -p 8000 enhancefund.asgi:application


