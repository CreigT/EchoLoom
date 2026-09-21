# Agent roster

Authority, escalation, and success metrics are part of the public contract. Changing them requires a versioned policy update.

| Agent | Purpose | Decides | Escalates when |
| --- | --- | --- | --- |
| CEO | Strategy, priorities, deadlocks | Spend above threshold, conflict winners | Existential / legal risk |
| Story Intake | Qualify raw submissions | Accept / reject / request more | Sensitive content |
| Narrative Architect | Scripts and episode structure | Creative structure in brand voice | Major narrative changes |
| Voice & Performance | Narration | Take selection in quality band | Clone quality fails |
| Sound Design & Music | Underscore + SFX | Musical choices in budget | License conflict |
| Rights & Compliance | IP, privacy, distribution | Block until cleared | Complex claims |
| Production Orchestrator | Masters and variants | Technical quality gates | Render failure |
| Marketplace | Publish and sell | Price band, channels | Pricing exceptions |
| Monetization | Revenue optimization | Package recommendations | Enterprise deals |
| Customer Success | Delivery and upsell | Standard outreach | Complaints |
| Analytics & Learning | System improvement | Non-breaking prompt updates | Architecture changes |
| Finance | Money movement | Standard collections | Disputes |
| Security & Fraud | Platform protection | Temporary holds | Confirmed fraud |

## Communication

Agents never call each other directly. They:

1. Receive an `Event`
2. Read `Project` state and vector memory
3. Emit one or more new events
4. Optionally attach artifacts

Event names use `domain.action` (`intake.completed`, `rights.blocked`, `ceo.priority_set`).

## Future agents (not in v0 runtime)

- Cultural Authenticity
- Merchandising
- Community
- Translation & Localization
- Impact Measurement
- Provenance
- Audience Co-Creation
- Sensory Extension
