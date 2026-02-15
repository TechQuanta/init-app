#!/bin/bash

echo ""
echo "🚀 Releasing py-create..."
echo ""

rm -rf build/ dist/ *.egg-info

python -m build
python -m twine upload dist/*

echo ""
echo "✔ Release complete 😌🔥"
echo ""
