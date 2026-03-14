#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:a:h}"
PRIVATE_DIR="$SCRIPT_DIR/../private"
KEY_FILE="$HOME/.config/vacations/private-key"
API_URL_FILE="$HOME/.config/vacations/api-url"

if [[ ! -f "$KEY_FILE" ]]; then
  echo "No key file found at $KEY_FILE"
  echo "Setup:"
  echo "  mkdir -p ~/.config/vacations"
  echo "  echo 'your-key' > ~/.config/vacations/private-key"
  echo "  echo 'https://your-site.netlify.app/.netlify/functions/trip' > ~/.config/vacations/api-url"
  exit 1
fi

KEY=$(cat "$KEY_FILE")

if [[ -f "$API_URL_FILE" ]]; then
  API_BASE=$(cat "$API_URL_FILE")
else
  echo "No API URL file found at $API_URL_FILE"
  exit 1
fi

TRIP="${1:-2026/trains-and-baseball}"

mkdir -p "$PRIVATE_DIR/$(dirname "$TRIP")"

echo "Pulling $TRIP..."
curl -sf "${API_BASE}?trip=${TRIP}&key=${KEY}" \
  -o "$PRIVATE_DIR/${TRIP}.json"

echo "Saved to private/${TRIP}.json"

echo "Validating..."
python3 "$SCRIPT_DIR/validate.py" "$PRIVATE_DIR/${TRIP}.json"
