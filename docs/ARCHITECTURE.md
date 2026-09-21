# EchoLoom Architecture

## Design principles

1. **Agents are specialists with explicit authority.** Each agent owns a bounded decision space and an escalation path.
2. **Events, not RPC spaghetti.** Agents publish facts to a shared bus. Subscribers react.
3. **Human gates only at legal, financial, and consent boundaries.**
4. **Every decision leaves a trace.** Reasoning, inputs, and outputs are audit-logged.
5. **Adapters isolate vendors.** LLM, TTS, music, payments, and distribution are swappable.

## Runtime topology

Customer Studio talks REST + SSE to a FastAPI gateway. The gateway publishes to an event bus. The orchestrator is a state machine with parallel forks, consensus, and human-in-the-loop pauses. Agents never call each other directly.

## Reasoning loop

Every significant agent action follows Perceive → Reason → Plan → Evaluate → Act → Verify → Learn, implemented in `backend/app/agents/base.py`.

## State model

A Project is the aggregate root, with status, risk score, gates (script approval, rights clearance, payment), artifacts, and an append-only event log.

## Parallelism

After a brief is accepted, Narrative Architect starts immediately while Rights begins a preliminary scan and Security scores fraud risk. After script approval, Voice and Sound Design run concurrently. Production waits for stems and clearance. Conflicts publish as `conflict.raised` and the CEO agent applies priority rules.

## Persistence

v0 uses in-memory state plus optional encryption. Production targets Postgres, a durable event store, LangGraph checkpointers, pgvector, and an encrypted object store.

## API surface

- POST /api/auth/demo
- POST /api/projects
- GET /api/projects
- GET /api/projects/{id}
- POST /api/projects/{id}/approve-script
- GET /api/projects/{id}/events
- GET /health

## Scaling path

Agent contracts stay stable from 1 to 1M projects. Scale by adding orchestrator workers, sharding project stores, region-local voice and rights models, and splitting API/worker fleets onto a durable bus.
