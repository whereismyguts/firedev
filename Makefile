up:
	docker compose up --build

down:
	docker compose down -v

health:
	curl -fsS http://localhost:8000/health | jq .
