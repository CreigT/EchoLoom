# Contributing to EchoLoom

Thank you for helping build a more human audio future.

## Ground rules

- Keep agent contracts stable. New agents should implement `BaseAgent`.
- Never log raw voice samples, government IDs, or unredacted PII.
- Critical outputs (masters, prices, legal clearances) need either multi-agent consensus or an explicit human gate.
- Prefer adapters over hard-coded vendors.

## Local development

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

## Project layout

```
backend/app/agents/     # one module per agent
backend/app/workflow/   # event bus + orchestrator
backend/app/api/        # HTTP + SSE
frontend/               # studio UI
docs/                   # architecture and policy
```

## Pull requests

1. Open an issue describing the change.
2. Keep PRs focused.
3. Add or update tests for workflow routing and security helpers.
4. Update docs if you change an agent contract.

## Code of conduct

Be precise, kind, and protective of storytellers. Harassment or extraction of personal recordings will result in a ban.
