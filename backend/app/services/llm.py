"""Vendor-isolated language adapter. Mock is the default so the app runs offline."""

from __future__ import annotations

from app.core.config import get_settings


class LLMAdapter:
    async def complete(self, system: str, prompt: str) -> str:
        raise NotImplementedError


class MockLLM(LLMAdapter):
    async def complete(self, system: str, prompt: str) -> str:
        lowered = prompt.lower()
        if "qualify" in lowered or "brief" in lowered:
            return (
                "TITLE: The Kitchen Table Archive\n"
                "ARC: origin → fracture → return → gift\n"
                "AUDIENCE: family + adjacent listeners who collect origin stories\n"
                "RUNTIME: 18-24 minutes\n"
                "NOTES: Strong intergenerational motif. Keep the kitchen as a recurring sound bed."
            )
        if "script" in lowered or "chapter" in lowered:
            return (
                "CHAPTER 1 — The Table\n"
                "Narration: Before anyone wrote it down, the story lived in the steam above a pot.\n\n"
                "CHAPTER 2 — The Fracture\n"
                "Narration: One winter the letters stopped. The house kept the recipe anyway.\n\n"
                "CHAPTER 3 — The Return\n"
                "Narration: A grandchild found the stained card and read it aloud to empty chairs.\n\n"
                "PRODUCTION: warm close-mic, wooden-room tone, sparse piano, no licensed pop cues."
            )
        if "price" in lowered:
            return "PACKAGE: Legacy Short-Form Audiobook\nPRICE: 149\nUPSSELL: Family sequel + private archive"
        return f"[mock:{system.split()[0].lower()}] {prompt[:240]}"


def get_llm() -> LLMAdapter:
    provider = get_settings().llm_provider
    if provider == "mock":
        return MockLLM()
    return MockLLM()
