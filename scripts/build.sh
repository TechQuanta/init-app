#!/bin/bash

echo ""
echo "📦 Building py-create package..."
echo ""

rm -rf build/ dist/ *.egg-info

python -m build

echo ""
echo "✔ Build complete 😌🔥"
echo ""
