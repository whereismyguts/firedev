#!/usr/bin/env bash
set -euo pipefail

# Render index.html from template with environment variables
envsubst '${NEXT_PUBLIC_FIREBASE_PROJECT_ID} ${NEXT_PUBLIC_FIREBASE_APP_ID} ${NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET} ${NEXT_PUBLIC_FIREBASE_API_KEY} ${NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN} ${NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID} ${NEXT_PUBLIC_FIREBASE_DATABASE_URL}' \
  < /usr/share/nginx/html/index.template.html \
  > /usr/share/nginx/html/index.html

exec "$@"
