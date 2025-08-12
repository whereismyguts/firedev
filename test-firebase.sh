#!/bin/bash
# Run this after creating Realtime Database to test connectivity

echo "🔄 Restarting backend to pick up database..."
docker compose -f /home/karmanov/projects/firedev/docker-compose.yml restart backend

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🩺 Testing health endpoint..."
curl -sS http://localhost:8000/health | jq .

echo ""
echo "✅ If you see 'firebase: true', the database is working!"
echo "❌ If you see 'firebase: false', check:"
echo "   - Database was created in Firebase Console"
echo "   - Database rules allow authenticated writes"
echo "   - Project ID matches: fireline-9wahd"
