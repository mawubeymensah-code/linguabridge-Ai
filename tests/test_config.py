from linguabridge.config import read_setting


def test_environment_overrides_host_secrets(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-only-env")
    assert read_setting("OPENAI_API_KEY", secrets_get=lambda *_: "test-only-host") == "test-only-env"


def test_host_secrets_are_used_when_environment_absent(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    assert read_setting("OPENAI_API_KEY", secrets_get=lambda *_: "test-only-host") == "test-only-host"


def test_missing_secrets_fall_back_to_demo(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    def absent(*_):
        raise FileNotFoundError()
    assert read_setting("OPENAI_API_KEY", secrets_get=absent) == ""


def test_non_string_config_uses_default(monkeypatch):
    monkeypatch.delenv("OPENAI_TRANSCRIPTION_MODEL", raising=False)
    assert read_setting("OPENAI_TRANSCRIPTION_MODEL", "whisper-1", lambda *_: {}) == "whisper-1"
