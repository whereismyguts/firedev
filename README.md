# Firedev stack

Dockerized Telegram bot + Flask backend + static web map with Firebase Realtime Database.

## Prerequisites

- Docker and Docker Compose
- Telegram bot token
- Firebase Realtime Database project and a Service Account JSON (Admin SDK)

## Setup

1. Copy your Firebase Admin SDK JSON to `secrets/firebase-adminsdk.json` (not committed).
2. Fill `.env` with:
   - NEXT_PUBLIC_FIREBASE_* values (already present)
   - TELEGRAM_BOT_TOKEN=your_token_here
3. Start services:

```sh
docker compose up --build
```

- Backend: <http://localhost:8000>
- Web Map: <http://localhost:8080>

## Health check / Firebase connectivity

- The backend exposes `GET /health` which attempts a tiny read from `locations/`.
- If it returns `{ status: "ok", firebase: true }`, the connection works.

## Notes

- The bot supports static and live locations. For live location, choose a category once; subsequent edits stream to the same record.
- Web page reads directly from Firebase using your public keys.
