#!/bin/sh
set -eu

if [ -z "${VITE_API_URL:-}" ]; then
    echo "VITE_API_URL must be set to the deployed API base URL." >&2
    exit 1
fi

api_base_url=${VITE_API_URL%/}
case "$api_base_url" in
    http://*/api|https://*/api) ;;
    *)
        echo "VITE_API_URL must be an HTTP(S) API URL ending in /api." >&2
        exit 1
        ;;
esac

escaped_api_url=$(printf '%s' "$VITE_API_URL" | sed 's/\\/\\\\/g; s/"/\\"/g')
printf 'window.STUDYMATE_API_URL = "%s";\n' "$escaped_api_url" \
    > /usr/share/nginx/html/runtime-config.js
