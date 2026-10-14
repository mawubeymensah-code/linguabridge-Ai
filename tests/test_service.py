from types import SimpleNamespace as NS
from unittest.mock import Mock
import json
import pytest
from linguabridge.service import MAX_BYTES, WorkflowError, demo_result, transcribe, translate, validate_audio


def client():
    return NS(audio=NS(transcriptions=NS(create=Mock(return_value=NS(text=" Bonjour ")))),
              responses=NS(create=Mock(return_value=NS(output_text=" Hello ", status="completed"))))


@pytest.mark.parametrize("name,data", [("file.exe", b"a"), ("file.wav", b""), ("file.mp3", b"x" * (MAX_BYTES + 1))])
def test_reject_invalid_audio(name, data):
    with pytest.raises(WorkflowError):
        validate_audio(name, data)


def test_source_and_private_filename():
    c = client()
    assert transcribe(c, "/private/my-name.MP3", b"audio", "French", "whisper-1") == "Bonjour"
    args = c.audio.transcriptions.create.call_args.kwargs
    assert args["language"] == "fr"
    assert args["file"].name == "recording.mp3"
    assert args["file"].getvalue() == b"audio"


def test_auto_detect_omits_language():
    c = client()
    transcribe(c, "a.wav", b"audio", "Auto detect", "whisper-1")
    assert "language" not in c.audio.transcriptions.create.call_args.kwargs


def test_translation_has_explicit_instructions_and_disables_storage():
    c = client()
    assert translate(c, "Bonjour", "English", "test-model") == "Hello"
    args = c.responses.create.call_args.kwargs
    assert args["input"] == "Bonjour" and args["store"] is False
    assert "English" in args["instructions"]


@pytest.mark.parametrize("status,expected", [(401, "denied"), (429, "quota"), (400, "input"), (500, "unavailable")])
def test_api_errors_never_leak_provider_details(status, expected):
    c = client()
    error = Exception("secret-provider-response")
    error.status_code = status
    c.audio.transcriptions.create.side_effect = error
    with pytest.raises(WorkflowError) as caught:
        transcribe(c, "a.wav", b"audio", "Auto detect", "whisper-1")
    assert expected in str(caught.value)
    assert "secret" not in str(caught.value)


def test_empty_transcript_is_actionable():
    c = client()
    c.audio.transcriptions.create.return_value = NS(text=" ")
    with pytest.raises(WorkflowError, match="No speech"):
        transcribe(c, "a.wav", b"audio", "Auto detect", "whisper-1")


def test_incomplete_translation_rejected():
    c = client()
    c.responses.create.return_value = NS(output_text="partial", status="incomplete")
    with pytest.raises(WorkflowError, match="incomplete"):
        translate(c, "Bonjour", "English", "test-model")


def test_bad_language_does_not_call_provider():
    c = client()
    with pytest.raises(WorkflowError):
        translate(c, "hello", "unknown", "test-model")
    c.responses.create.assert_not_called()


def test_demo_export_preserves_unicode_and_marks_demo():
    result = demo_result("Japanese")
    assert json.loads(result.to_json())["demo"] is True
    assert "こんにちは" in result.to_json()
