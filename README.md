# EVITO n8n environment

This stack builds a custom n8n image with Python available for workflow scripts and persists the built-in SQLite database. All paths are absolute and intended for Podman Compose.

## Folder layout
- `/home/superfuru/EVITO/infra` – Dockerfile and podman compose definition
- `/home/superfuru/EVITO/data/n8n` – persistent n8n application data (SQLite, credentials, sessions)
- `/home/superfuru/EVITO/services/risk` – mounted into `/data/scripts` inside the container

## Build
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml build`

## Start / Stop
- Start: `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml up -d`
- Stop: `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml down`

## Exec into the container as root
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml exec -u 0 -T n8n /bin/sh`

## Test Python inside n8n container
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml exec -T n8n python3 -V`
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml exec -T n8n python3 -c "import pandas, yfinance, requests; print('python ready')"`

## Verify risk_bot is available
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml exec -T n8n ls -l /data/scripts`
- `podman compose -f /home/superfuru/EVITO/infra/docker-compose.yml exec -T n8n python3 /data/scripts/risk_bot.py "TSLA"`

## Import workflows
- Open `http://localhost:5678` in your browser after the stack is running.
- Use the n8n editor menu → *Import from File* to upload your exported workflow JSON, or paste JSON via *Import from Clipboard*.
- Sessions persist because SQLite data is stored in `/home/superfuru/EVITO/data/n8n`.
