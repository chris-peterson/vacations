#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:a:h}"
PRIVATE_DIR="$SCRIPT_DIR/../private"

TRIP="${1:-2026/trains-and-baseball}"
JSON_PATH="$PRIVATE_DIR/${TRIP}.json"

if [[ ! -f "$JSON_PATH" ]]; then
  echo "No file found at $JSON_PATH"
  exit 1
fi

echo "Validating..."
python3 "$SCRIPT_DIR/validate.py" "$JSON_PATH"

echo "Checking for conflicts..."
python3 "$SCRIPT_DIR/check_conflicts.py" "$JSON_PATH"

SITE_ID_FILE="$HOME/.config/vacations/netlify-site-id"
if [[ ! -f "$SITE_ID_FILE" ]]; then
  echo "No Netlify site ID found at $SITE_ID_FILE"
  echo "Setup: echo 'your-site-id' > ~/.config/vacations/netlify-site-id"
  exit 1
fi

SITE_ID=$(cat "$SITE_ID_FILE")

echo "Deploying private data to Netlify..."
npx netlify-cli deploy --dir="$PRIVATE_DIR" --site="$SITE_ID" --prod

echo "Done."
