#!/bin/bash

INIT_FILE="create_app/__init__.py"

echo ""
echo "🔎 Current version:"
grep "__version__" $INIT_FILE
echo ""

read -p "New version → " NEW_VERSION

sed -i "s/__version__ = \".*\"/__version__ = \"$NEW_VERSION\"/" $INIT_FILE

echo ""
echo "✔ Version updated → $NEW_VERSION 😌🔥"
echo ""
