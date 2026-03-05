# Set Up Cloudflare Tunnel

This page describes how to create a Cloudflare Tunnel to expose the MCP server to the internet without port forwarding.

## Prerequisites

- A [Cloudflare account](https://dash.cloudflare.com)
- A registered domain (any registrar)
- Docker and Docker Compose installed on the server
- `CLOUDFLARE_TUNNEL_TOKEN` available to add to the `.env` file on the server
- A GitHub account (for OAuth)
- [uv](https://docs.astral.sh/uv/) installed (for local development)

## Local Development Setup

Install dependencies with uv:

```bash
uv sync
```

Run the server locally:

```bash
uv run python passage_of_time_mcp.py
```

Run tests:

```bash
uv run pytest
```

The server starts on `http://0.0.0.0:8000/mcp`.

## Create a GitHub OAuth App

Claude.ai Remote MCP requires OAuth authentication. This server uses GitHub as the OAuth provider.

1. Go to [GitHub](https://github.com) → **Settings** → **Developer settings** → **OAuth Apps** → **New OAuth App**.

1. Fill in the fields:
   - **Application name**: `passage-of-time-mcp` (or any name)
   - **Homepage URL**: `https://<subdomain>.<domain>`
   - **Authorization callback URL**: `https://<subdomain>.<domain>/auth/callback`

1. Click **Register application**.

1. On the app page, copy the **Client ID**. Then click **Generate a new client secret** and copy the secret.

## Add the domain to Cloudflare

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com) → **Add a site** → enter your domain name → select a plan.

1. Cloudflare scans existing DNS records and shows two nameservers (e.g. `emma.ns.cloudflare.com`, `ivan.ns.cloudflare.com`). Copy both.

1. Log in to your domain registrar (e.g. Gabia, Hosting.kr, Namecheap) and open the nameserver settings for the domain.

1. Replace the current nameservers with the two Cloudflare nameservers copied in the previous step.

   > **Important:** Nameserver propagation can take up to 48 hours, though it usually completes within a few minutes.

1. Back in the Cloudflare dashboard, click **Check nameservers**. Once propagation completes, the domain status changes to **Active**.

1. In the Cloudflare dashboard, go to **DNS** → **Records** → **Add record**. Add the records needed for your subdomain (Cloudflare Tunnel creates a CNAME automatically when you add a public hostname in the tunnel config, so manual DNS records are only needed for non-tunnel services).

## Create the tunnel

1. Go to [Cloudflare Dashboard](https://one.dash.cloudflare.com) → **Networks** → **Connectors** → **Create a tunnel**.

1. Select **Cloudflared** as the connector type, enter a tunnel name (e.g. `passage-of-time-mcp`), then click **Save tunnel**.

1. Copy the tunnel token from the install command shown on screen (the long string at the end of `cloudflared service install <token>`). Save it for the `.env` file.

1. Under **Public Hostnames**, add a route:
   - Subdomain: your chosen subdomain (e.g. `mcp`)
   - Domain: your domain
   - Service: `http://time-mcp:8000`

   > **Important:** The service URL must use the Compose service name `time-mcp`, not `localhost`. Both containers share the `internal` bridge network defined in `docker-compose.yml`.

1. Click **Save hostname**.
   The tunnel status will remain **Inactive** until the `cloudflared` container starts.

## Add variables to the server

On the server, copy `.env.example` to `.env` at the project root and fill in all values:

```bash
cp .env.example .env
```

```env
CLOUDFLARE_TUNNEL_TOKEN=<token from Cloudflare Zero Trust>
GITHUB_CLIENT_ID=<GitHub OAuth App client ID>
GITHUB_CLIENT_SECRET=<GitHub OAuth App client secret>
MCP_BASE_URL=https://<subdomain>.<domain>
```

| Variable | Description |
|----------|-------------|
| `CLOUDFLARE_TUNNEL_TOKEN` | Tunnel token from Cloudflare Zero Trust |
| `GITHUB_CLIENT_ID` | GitHub OAuth App client ID |
| `GITHUB_CLIENT_SECRET` | GitHub OAuth App client secret |
| `MCP_BASE_URL` | Public HTTPS URL of this server (no trailing slash) |

## Start the containers

```bash
docker compose -f docker/docker-compose.yml --env-file .env up -d
```

The `cloudflared` service depends on the `time-mcp` health check passing, so it starts roughly 15–45 seconds after Docker Compose begins. Once both containers are running, the tunnel status in the Cloudflare dashboard changes to **Healthy**.

## Connect to Claude.ai

1. In Claude.ai, go to **Settings** → **Integrations** → **Add integration** → **Custom**.
1. Enter the server URL: `https://<subdomain>.<domain>/mcp`
1. Claude.ai will redirect to GitHub for authentication. Approve the OAuth request.
1. Save and enable the time-related tools.

## Verify

1. Open the Cloudflare Zero Trust dashboard → **Networks** → **Tunnels** — confirm the tunnel shows **Healthy**.
1. Connect from Claude.ai using the public URL ending in `/mcp`.
1. Ask Claude for the current time to confirm the `current_datetime` tool responds.

## Remove

1. Stop and remove the containers:

   ```bash
   docker compose -f docker/docker-compose.yml --env-file .env down
   ```

1. In the Cloudflare Zero Trust dashboard → **Networks** → **Tunnels**, select the tunnel → **Delete**.
1. In GitHub → **Settings** → **Developer settings** → **OAuth Apps**, delete the OAuth App.
