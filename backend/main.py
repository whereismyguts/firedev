import os
import json
import time
from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, db

app = Flask(__name__)

FIREBASE_DATABASE_URL = os.getenv("FIREBASE_DATABASE_URL")
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if not FIREBASE_DATABASE_URL:
    raise RuntimeError("FIREBASE_DATABASE_URL env var is required")
if not GOOGLE_APPLICATION_CREDENTIALS or not os.path.exists(GOOGLE_APPLICATION_CREDENTIALS):
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS must point to a readable service account JSON (mounted as a Docker secret)")

if FIREBASE_DATABASE_URL and not FIREBASE_DATABASE_URL.endswith('/'):
    FIREBASE_DATABASE_URL = FIREBASE_DATABASE_URL + '/'

if not firebase_admin._apps:
    cred = credentials.Certificate(GOOGLE_APPLICATION_CREDENTIALS)
    firebase_admin.initialize_app(cred, {
        'databaseURL': FIREBASE_DATABASE_URL
    })

ref = db.reference('locations')


@app.get('/health')
def health():
    try:
        # Write/Delete probe to confirm connectivity and permissions
        probe_ref = db.reference('_health_probe')
        probe_ref.set({'ts': time.time()})
        probe_ref.delete()
        return jsonify({"status": "ok", "firebase": True}), 200
    except Exception as e:
        return jsonify({"status": "error", "firebase": False, "message": str(e)}), 500


@app.post('/report')
def report():
    try:
        payload = request.get_json(force=True)
        required = ["category", "lat", "lon", "user", "timestamp", "action"]
        missing = [k for k in required if k not in payload]
        if missing:
            return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400
        # Basic type coercion
        payload["lat"] = float(payload["lat"])  # may raise
        payload["lon"] = float(payload["lon"])  # may raise
        ref.push(payload)
        return jsonify({"status": "added"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.put('/report/<item_id>')
def report_put(item_id: str):
    """Create or update a fixed ID entry for live location tracking."""
    try:
        payload = request.get_json(force=True)
        required = ["category", "lat", "lon", "user", "timestamp", "action"]
        missing = [k for k in required if k not in payload]
        if missing:
            return jsonify({"error": f"missing fields: {', '.join(missing)}"}), 400
        payload["lat"] = float(payload["lat"])  # may raise
        payload["lon"] = float(payload["lon"])  # may raise
        db.reference(f"locations/{item_id}").set(payload)
        return jsonify({"status": "upserted", "id": item_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(host='0.0.0.0', port=port)
