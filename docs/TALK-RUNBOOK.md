### Fueling Manufacturing Integration With AI & Ignition Containers — Talk Runbook (45 min)

- **Event**: Central Theater
- **Time**: 3:15 PM – 4:00 PM PDT / 4:15 PM – 5:00 PM Your local
- **Speakers**: You (Lead), Colleague (Co‑presenter; ~33% contribution)

---

### Goals
- **Show a ready-to-run Ignition development stack** using Docker (gateway + infra).
- **Demonstrate AI-assisted development** with Cursor and Claude Code on a real task.
- **Walk through Ignition Git module workflow** for project collaboration.
- **Highlight observability and integration** via Kong, Redis, Postgres, MQTT, and Grafana.

---

### Audience Takeaways
- Start an Ignition dev environment in minutes with containers.
- Use Git-backed projects for team workflows.
- Leverage AI coding assistants to accelerate Ignition scripting and integration code.

---

### Agenda (timed)
1) 0:00–3:00 — Welcome and problem framing (Lead)
   - Why containers for SCADA/MES dev; reproducibility; onboarding speed.
2) 3:00–8:00 — Architecture overview (Lead)
   - `docker-compose.yml` services: Ignition, Kong, Postgres, Redis, MQTT, Grafana.
   - Git module + `gw-init/git.yaml` for project sync.
3) 8:00–18:00 — Live bring-up: Ready-to-go stack (Lead driving, Colleague narrates)
   - Preflight, compose up, first-run tasks, accept Git module cert.
   - Verify gateway at `https://localhost:9043` and Kong/Grafana UIs.
4) 18:00–28:00 — Dev workflow in Ignition with Git (Colleague driving)
   - Project pull, branch switch, commit/push, and how to work inside container if needed.
5) 28:00–38:00 — AI-assisted development demo (Lead + Colleague)
   - Use Cursor/Claude to add a small feature (e.g., MQTT tag write + API call via Kong).
   - Show test, logs, and Grafana dashboard.
6) 38:00–43:00 — Operations: reset, logs, troubleshooting, VPN note (Colleague)
7) 43:00–45:00 — Q&A and resources (Lead)

---

### Live Demo Script

Prereqs
- Docker Desktop running.
- GitHub token with `read:packages` and repo access.
- `.env` pulled via dotenv-vault or set manually (see `README.md`).
- `secrets/GATEWAY_ADMIN_PASSWORD` and `secrets/GIT_USER_TOKEN` files exist.

Commands (copy/paste)
```bash
# From repo root
pwd

# 1) Preflight
./install.sh || true
./test-connectivity.sh || true

# 2) Pull env (optional if already present)
npm install -g dotenv-vault@latest || true
npx dotenv-vault@latest pull || true

# 3) Bring up core stack
docker compose up -d

# 4) Tail health a few seconds
docker ps | cat
sleep 5

# 5) Open key UIs (Mac)
open https://localhost:9043   # Ignition (HTTPS)
open http://localhost:3000    # Grafana
open http://localhost:8000    # Kong proxy (if route used)
open http://localhost:15672   # RabbitMQ mgmt
open http://localhost:19999   # Netdata
```

First‑run checks in Gateway (narrate clicks)
- Configuration → Modules → Quarantined Modules → Accept Git module
- Watch projects auto-pull (from `gw-init/git.yaml`).

Optional: Exec inside gateway (for Git ops)
```bash
docker exec -it $(docker ps --filter name=ignition -q | head -n1) bash
cd /usr/local/bin/ignition/data/projects
ls -la
git status
```

Small Feature for AI Demo
- Goal: Create a button that publishes a payload to MQTT and writes a tag.
- Steps:
  - In Designer, add a view/window with a button.
  - Use Cursor/Claude to draft Jython script to publish to MQTT Engine tag path and log result.
  - Optionally call backend over Kong (`http://localhost:8000/...`) and display response in a label.

Observability
- Show Grafana dashboards (`monitoring/grafana/...`).
- Show container metrics via cAdvisor and Netdata.

Teardown / Reset
```bash
# Stop
docker compose down

# Reset volumes (demo-only)
docker compose down -v
```

---

### Roles and Hand‑offs
- Lead
  - Frame problem, architecture, and drive stack bring-up.
  - Pair with AI to implement the feature.
- Colleague (~33% live)
  - Walk through Git workflow in Ignition and inside container.
  - Cover ops: logs, restarts, resets, VPN callout.
  - Co-drive AI demo script refinement and quick test.

Time Cues
- 8 min: stack up and gateway reachable
- 18 min: Git module accepted and project visible
- 30–35 min: feature working end-to-end

---

### Quick Reference Links
- `README.md` → full setup notes, git.yaml details.
- `docker-compose.yml` → services and ports.
- `gw-init/git.yaml` → project sources/branches.
- `monitoring/` → Prometheus + Grafana provisioning.

---

### Contingencies
- If Git token fails: verify `secrets/GIT_USER_TOKEN` and `.env GIT_USER_TOKEN`.
- If modules quarantined: accept Git module; restart container if needed.
- If ports busy: stop conflicting services or change env vars and restart.



