# EchoLoom

**Turn raw stories into living audio.**

EchoLoom converts personal stories, voice notes, family recordings, and brand narratives into polished audiobooks, immersive podcasts, and multimedia story packages. A swarm of specialized AI agents handles intake, narrative design, voice, sound, rights, production, distribution, and monetization.

> One-sentence mission: EchoLoom turns raw personal stories into professionally produced audio through a swarm of specialized AI agents that handle creation, rights clearance, production, distribution, and monetization.

## Why this exists

Most people and small organizations sit on valuable stories that never become listenable products. Professional scripting, voice direction, music licensing, cover design, distribution, and rights management are expensive, slow, and fragmented. EchoLoom collapses that stack into an auditable multi-agent workflow with human gates only where law, money, or consent require them.

## Who it is for

- Individuals creating memoirs and family legacies
- Small-to-medium businesses sharing origin stories and thought leadership
- Education (oral history) and nonprofits

## What is in this repository

This is the **v0 foundation**: a running application, not a slide deck.

| Layer | What you get |
| --- | --- |
| Agent runtime | Perceive → Reason → Plan → Evaluate → Act → Verify → Learn loop |
| Workflow engine | Event-driven orchestrator with parallel creative work and rights gates |
| Backend API | FastAPI with project intake, live event stream, approvals, artifacts |
| Client studio | Single-page studio to submit a story and watch agents collaborate |
| Security | JWT auth, PII flags, encryption helpers, immutable audit log |
| Ops | Docker Compose, health checks, pytest suite, GitHub Actions |

Production voice cloning, marketplace connectors, and payment rails are stubbed behind provider adapters so the system runs locally with no paid keys.

## Architecture at a glance

```
Customer Studio  ──REST + SSE──►  FastAPI gateway
                                      │
                                 Event Bus
                                      │
        ┌──────────────┬──────────────┼──────────────┬──────────────┐
        │              │              │              │              │
     Intake      Narrative       Voice &        Rights &      Production
                 Architect       Sound          Compliance    Orchestrator
                                      │
                          Marketplace / Finance / Success
                                      │
                              Analytics & Learning
                                      │
                                 CEO Agent
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/AGENTS.md](docs/AGENTS.md).

## Quick start

### Prerequisites

- Python 3.11+
- Optional: Docker + Docker Compose

### Local (no Docker)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env
uvicorn app.main:app --reload --app-dir . --port 8000
```

Open http://localhost:8000 for the studio UI and http://localhost:8000/docs for the API.

### Docker

```bash
docker compose up --build
```

### Run tests

```bash
cd backend
pytest -q
```

## Customer workflow (implemented)

1. Customer submits text or a voice-note transcript in the studio.
2. **Story Intake** qualifies the brief, scores risk, and detects PII / sensitivity.
3. **Narrative Architect** writes a chaptered script and production notes.
4. Customer approves the script (human gate).
5. **Voice** and **Sound Design** work in parallel.
6. **Rights & Compliance** can block until clearance.
7. **Production Orchestrator** masters delivery files.
8. **Marketplace**, **Finance**, and **Customer Success** publish, invoice, and follow up.
9. **Analytics** records outcomes; **CEO** resolves conflicts.

## Security stance

Sensitive family and brand stories are the product. v0 includes:

- Passwordless-ready JWT session model
- PII detection on intake
- Encrypted artifact envelopes at rest (Fernet when `ENCRYPTION_KEY` is set)
- Immutable audit events for every agent decision
- Role-scoped project access

Details: [docs/SECURITY.md](docs/SECURITY.md).

## Roadmap

See [docs/ROADMAP.md](docs/ROADMAP.md) for 30 / 60 / 90 day plan, living-chapter experiments, and known risks (voice-consent disputes, platform policy, homogenization).

## Contributing

Issues and PRs are welcome. Start with [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT. See [LICENSE](LICENSE).
