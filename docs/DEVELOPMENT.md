# Development Guide

## Requirements
- Windows 11
- Docker Desktop with WSL2 backend
- Git
- Node.js 20 LTS or newer
- Python 3.12 (optional for running API outside Docker)

## Start
1. Copy `.env.example` to `.env`.
2. Change local passwords in `docker-compose.yml` and `.env` before sharing the machine.
3. Run `docker compose up --build -d`.
4. Run `cd frontend-web && npm install && npm run dev`.
5. Open `http://localhost:5173`; API docs: `http://localhost:8000/docs`; Keycloak: `http://localhost:8080`.

The API starts with `AUTH_ENABLED=false` for local scaffolding only. Never deploy this mode. The local API development principal is not a real authenticated user.
