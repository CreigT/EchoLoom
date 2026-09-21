# Security

Family histories and unreleased brand stories are high-sensitivity assets.

## Controls in v0

- **Auth**: JWT sessions. Demo login issues a scoped token. Production should be passwordless + hardware keys.
- **Authorization**: project ownership checks on every mutating route.
- **PII**: regex + heuristic detector on intake; findings stored as flags, not raw echoes in later prompts when redaction is on.
- **Encryption**: optional Fernet envelope for stored artifacts when `ENCRYPTION_KEY` is present.
- **Audit**: append-only event log with actor, action, and reasoning summary.
- **Uploads**: size cap via `MAX_UPLOAD_MB`.
- **Headers**: restrictive baseline CORS and no-cache on project payloads.

## Threats we take seriously

1. Voice-clone consent disputes and deepfakes
2. Cross-project data leakage through shared model context
3. Payment fraud against escrow / royalty splits
4. Prompt injection hidden in submitted memoirs
5. Retention beyond the customer's "Forever Archive" agreement

## Rules for contributors

- Do not send raw audio to third-party APIs without an explicit customer grant recorded on the project.
- Do not use customer stories as training data unless the contract says so.
- Default-deny distribution. Marketplace publishing is opt-in.
- Treat rejection reasons as potentially sensitive (they can reveal family conflict).

## Production backlog

- Object-store SSE-KMS
- Customer-managed keys
- Immutable WORM audit bucket
- GDPR/CCPA export and erasure workflows
- Hardware-backed session keys
- Continuous voice-authenticity scoring
