#!/bin/bash

echo ""
echo "🧹 Cleaning py-create workspace..."
echo ""

rm -rf build/
rm -rf dist/
rm -rf *.egg-info
find . -name "__pycache__" -type d -exec rm -rf {} +

echo ""
echo "✔ Clean workspace 😌🔥"
echo ""
