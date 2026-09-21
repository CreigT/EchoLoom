from __future__ import annotations

from app.agents.base import AgentResult, BaseAgent
from app.models.domain import Artifact, Event, Project, ProjectStatus
from app.security.pii import detect_pii


class CEOAgent(BaseAgent):
    name = "ceo"
    purpose = "Prioritize work and resolve cross-agent deadlocks"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        blocked = project.status == ProjectStatus.BLOCKED
        summary = (
            "CEO holds production until rights or security clear."
            if blocked
            else "CEO ranks this project as active revenue work."
        )
        return AgentResult(events=[self.event(project, "ceo.priority_set", summary, {"blocked": blocked})])


class IntakeAgent(BaseAgent):
    name = "intake"
    purpose = "Convert raw submissions into structured briefs"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        flags = detect_pii(project.raw_story)
        project.risk_flags = flags
        project.risk_score = min(100, 8 * len(flags) + max(12, min(len(project.raw_story) // 80, 40)))
        high = any(f.severity == "high" for f in flags)
        draft = await self.llm.complete(
            "You are the EchoLoom Story Intake agent.",
            f"Qualify this story into a brief:\n{project.raw_story}\nStyle: {project.style_preferences}",
        )
        brief = Artifact(kind="brief", title="Project brief", content=draft, metadata={"risk": project.risk_score})
        if high and project.risk_score >= 40:
            return AgentResult(
                artifacts=[brief],
                status=ProjectStatus.BLOCKED.value,
                events=[
                    self.event(
                        project,
                        "intake.escalated",
                        "Sensitive content flagged for legal review",
                        {"flags": [f.model_dump() for f in flags]},
                    )
                ],
            )
        return AgentResult(
            artifacts=[brief],
            status=ProjectStatus.BRIEFING.value,
            events=[
                self.event(
                    project,
                    "intake.completed",
                    "Submission qualified and briefed",
                    {"risk_score": project.risk_score, "flags": [f.code for f in flags]},
                )
            ],
        )


class NarrativeArchitectAgent(BaseAgent):
    name = "architect"
    purpose = "Craft scripts and episode structures"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        brief = project.artifact("brief")
        script_text = await self.llm.complete(
            "You are the EchoLoom Narrative Architect.",
            f"Write a chaptered narration script.\nBrief:\n{brief.content if brief else project.raw_story}",
        )
        script = Artifact(
            kind="script",
            title="Narration script",
            content=script_text,
            metadata={"needs_approval": True},
        )
        return AgentResult(
            artifacts=[script],
            status=ProjectStatus.AWAITING_APPROVAL.value,
            events=[self.event(project, "architect.script_ready", "Script ready for customer approval")],
        )


class VoiceAgent(BaseAgent):
    name = "voice"
    purpose = "Generate or select narration"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        script = project.artifact("script")
        take = Artifact(
            kind="voice_track",
            title="Narration take A",
            content="[synthetic-voice:warm-baritone] " + (script.content[:500] if script else ""),
            metadata={"provider": "mock", "naturalness": 0.91, "consent": "required-at-clone"},
        )
        return AgentResult(artifacts=[take], events=[self.event(project, "voice.rendered", "Primary narration take rendered")])


class SoundDesignAgent(BaseAgent):
    name = "sound"
    purpose = "Create underscoring and effects with license metadata"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        stems = Artifact(
            kind="stems",
            title="Score and room tone",
            content="beds: soft piano in G; sfx: kettle, chair scrape, paper card; license: original-generated",
            metadata={"license": "original", "budget_band": "standard"},
        )
        return AgentResult(artifacts=[stems], events=[self.event(project, "sound.mixed", "Original score and SFX stems prepared")])


class RightsAgent(BaseAgent):
    name = "rights"
    purpose = "Clear IP, privacy, and distribution rights"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        third_party = "copyright" in project.raw_story.lower() or "lyrics" in project.raw_story.lower()
        if third_party:
            return AgentResult(
                status=ProjectStatus.BLOCKED.value,
                events=[self.event(project, "rights.blocked", "Possible third-party lyrics or copyrighted material — production held")],
            )
        package = Artifact(
            kind="clearance",
            title="Clearance package",
            content="Customer declaration accepted. No third-party matches. Distribution: private + optional public.",
            metadata={"jurisdictions": ["US"], "voice_clone_consent": "pending-if-clone"},
        )
        return AgentResult(
            artifacts=[package],
            gate_updates={"rights_clearance": True},
            events=[self.event(project, "rights.cleared", "Rights package issued")],
        )


class ProductionAgent(BaseAgent):
    name = "production"
    purpose = "Assemble masters and delivery variants"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        if not project.artifact("voice_track") or not project.artifact("stems"):
            return AgentResult(events=[self.event(project, "production.waiting", "Waiting on stems")])
        if not project.gates.get("rights_clearance"):
            return AgentResult(
                status=ProjectStatus.CLEARING.value,
                events=[self.event(project, "production.waiting", "Waiting on rights clearance")],
            )
        master = Artifact(
            kind="master",
            title="Delivery master",
            content="master.wav · loudness -18 LUFS · chapters marked · captions sidecar",
            metadata={"spec": "audiobook-v1", "variants": ["podcast", "trailer"]},
        )
        return AgentResult(
            artifacts=[master],
            status=ProjectStatus.PUBLISHING.value,
            events=[self.event(project, "production.mastered", "Master and variants passed quality gates")],
        )


class MarketplaceAgent(BaseAgent):
    name = "marketplace"
    purpose = "Publish private or public listings"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        listing = Artifact(
            kind="listing",
            title="Private gallery listing",
            content=f"https://studio.echoloom.local/gallery/{project.id}",
            metadata={"visibility": "private", "channels": ["private-gallery"]},
        )
        return AgentResult(artifacts=[listing], events=[self.event(project, "marketplace.listed", "Private listing published")])


class MonetizationAgent(BaseAgent):
    name = "monetization"
    purpose = "Recommend price and packages"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        rec = await self.llm.complete("Pricing agent", f"Price this project: {project.title} {project.package_type}")
        artifact = Artifact(kind="pricing", title="Package recommendation", content=rec)
        return AgentResult(artifacts=[artifact], events=[self.event(project, "monetization.priced", "Price band recommended")])


class FinanceAgent(BaseAgent):
    name = "finance"
    purpose = "Invoice and collect"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        invoice = Artifact(
            kind="invoice",
            title="Project invoice",
            content="Invoice draft $149 · escrow ready · royalty split 80/20 if public sale",
            metadata={"amount": 149, "currency": "USD", "status": "draft"},
        )
        return AgentResult(artifacts=[invoice], events=[self.event(project, "finance.invoiced", "Draft invoice created")])


class CustomerSuccessAgent(BaseAgent):
    name = "success"
    purpose = "Deliver files and follow up"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        note = Artifact(
            kind="delivery",
            title="Delivery note",
            content="Masters delivered to private gallery. Review requested. Sequel offer queued.",
        )
        return AgentResult(
            artifacts=[note],
            status=ProjectStatus.DELIVERED.value,
            gate_updates={"payment": True} if project.gates.get("rights_clearance") else {},
            events=[self.event(project, "success.delivered", "Customer delivery sequence started")],
        )


class AnalyticsAgent(BaseAgent):
    name = "analytics"
    purpose = "Record outcomes for later learning"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        return AgentResult(
            events=[
                self.event(
                    project,
                    "analytics.recorded",
                    "Cycle metrics stored",
                    {
                        "cycle_events": len(project.events),
                        "risk_score": project.risk_score,
                        "approved": project.gates.get("script_approval"),
                    },
                )
            ]
        )


class SecurityAgent(BaseAgent):
    name = "security"
    purpose = "Detect anomalous submissions and deepfake risk"

    async def act(self, project: Project, trigger: Event, perception: dict) -> AgentResult:
        suspicious = project.raw_story.count("http") > 3
        if suspicious:
            return AgentResult(
                status=ProjectStatus.BLOCKED.value,
                events=[self.event(project, "security.hold", "Anomalous link density — temporary hold")],
            )
        return AgentResult(events=[self.event(project, "security.cleared", "No fraud markers on intake")])


AGENT_REGISTRY: dict[str, BaseAgent] = {
    "ceo": CEOAgent(),
    "intake": IntakeAgent(),
    "architect": NarrativeArchitectAgent(),
    "voice": VoiceAgent(),
    "sound": SoundDesignAgent(),
    "rights": RightsAgent(),
    "production": ProductionAgent(),
    "marketplace": MarketplaceAgent(),
    "monetization": MonetizationAgent(),
    "finance": FinanceAgent(),
    "success": CustomerSuccessAgent(),
    "analytics": AnalyticsAgent(),
    "security": SecurityAgent(),
}
