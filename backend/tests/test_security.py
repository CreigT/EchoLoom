from app.security.pii import detect_pii


def test_detects_email_and_sensitive_topic():
    flags = detect_pii("Write to jane@example.com about the classified trade secret.")
    codes = {f.code for f in flags}
    assert "pii_email" in codes
    assert "sensitive_topic" in codes
