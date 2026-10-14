from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).parents[1] / "app.py")


def test_demo_and_language_change_clear_stale_results():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    at.button[0].click().run()
    assert not at.exception
    assert "Bonjour" in at.session_state["result"].translation
    at.selectbox[1].select("Spanish").run()
    assert "result" not in at.session_state
    at.button[0].click().run()
    assert "¡Hola!" in at.session_state["result"].translation


def test_live_without_key_is_disabled(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    at = AppTest.from_file(APP).run()
    at.sidebar.radio[0].set_value("Live API").run()
    assert not at.exception
    assert at.button[0].disabled
    assert any("OPENAI_API_KEY" in warning.value for warning in at.warning)
