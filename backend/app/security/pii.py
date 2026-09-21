import re

from app.models.domain import RiskFlag

EMAIL = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.I)
PHONE = re.compile(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b")
SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
SENSITIVE = re.compile(
    r"\b(abuse|assault|suicide|minor|classified|trade secret|ssn|passport)\b",
    re.I,
)


def detect_pii(text: str) -> list[RiskFlag]:
    flags: list[RiskFlag] = []
    if EMAIL.search(text):
        flags.append(RiskFlag(code="pii_email", severity="medium", detail="Email address detected"))
    if PHONE.search(text):
        flags.append(RiskFlag(code="pii_phone", severity="medium", detail="Phone number detected"))
    if SSN.search(text):
        flags.append(RiskFlag(code="pii_ssn", severity="high", detail="SSN-like pattern detected"))
    if SENSITIVE.search(text):
        flags.append(
            RiskFlag(
                code="sensitive_topic",
                severity="high",
                detail="Submission may include sensitive or regulated subject matter",
            )
        )
    return flags
