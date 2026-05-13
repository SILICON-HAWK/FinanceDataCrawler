# Remote Container Setup

Add a Docker container to the server so Caddy auto-discovers it and routes traffic to it. The only shared resource is the `web` Docker network — your compose file can live anywhere on the server.

## How It Works

```
:80 ──► caddy (docker-proxy) ──► web network ──► your-container
              │
          reads labels
          on your container
```

Caddy (running as `lucaslorentz/caddy-docker-proxy`) watches the Docker API for containers on the `web` network and configures itself from their labels. No Caddyfile editing required.

## The `web` Network

The network is `attachable: true`, so any container — from any `compose.yml` anywhere on disk, or from `docker run` — can join it.

### In a compose file

```yaml
networks:
  web:
    external: true
```

### docker run

```bash
docker run -d --network web ...
```

## Caddy Labels

| Label | Purpose | Example |
|---|---|---|
| `caddy` | Hostname or address Caddy listens on | `myapp.local` or `:80` |
| `caddy.reverse_proxy` | Upstream endpoint template | `{{upstreams 3000}}` |

`{{upstreams PORT}}` expands to the container's IP on the `web` network at the given internal port. Do not use the published host port here.

### Port exposure

- **Caddy-routed only:** no `ports:` needed — Caddy reaches the container via the internal network
- **Direct access needed:** publish the port with `ports:` (e.g., `11434:11434` for external API clients)

## Compose Examples

### Minimal (Caddy-routed only)

```yaml
# ~/anywhere/compose.yml
services:
  myapp:
    image: myapp:latest
    networks:
      - web
    labels:
      caddy: myapp.local
      caddy.reverse_proxy: "{{upstreams 3000}}"
    restart: unless-stopped

networks:
  web:
    external: true
```

```bash
cd ~/anywhere && docker compose up -d
```

### With direct port and GPU

```yaml
services:
  mygpu-app:
    image: mygpu-app:latest
    ports:
      - 8000:8000
    networks:
      - web
    labels:
      caddy: mygpu-app.local
      caddy.reverse_proxy: "{{upstreams 8000}}"
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]
    restart: unless-stopped

networks:
  web:
    external: true
```

Requires `nvidia-container-toolkit` on the host.

## docker run

```bash
docker run -d \
  --name myapp \
  --network web \
  --label "caddy=myapp.local" \
  --label "caddy.reverse_proxy={{upstreams 3000}}" \
  --restart unless-stopped \
  myapp:latest
```

## `.local` Resolution

Caddy routes by hostname, so `myapp.local` must resolve to `127.0.0.1` on any machine that needs to reach it by name:

```bash
echo '127.0.0.1  myapp.local' | sudo tee -a /etc/hosts
```

For remote access, use the Tailscale IP + published port, or set up Tailscale Serve.

## Volumes

```yaml
services:
  myapp:
    volumes:
      - myapp_data:/data

volumes:
  myapp_data:
```

## Health Checks

```yaml
services:
  myapp:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 5s
      retries: 3
```

Caddy stops routing to unhealthy containers.

## Quick Reference

```bash
# Start your service
cd /path/to/your/compose && docker compose up -d

# View logs
docker compose -f /path/to/your/compose/compose.yml logs -f

# Restart
docker compose -f /path/to/your/compose/compose.yml restart

# Remove
docker compose -f /path/to/your/compose/compose.yml rm -sf
```
