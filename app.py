"""Run with `streamlit run app.py`. Live requests are explicit and consent-gated."""
import hashlib
import os
import streamlit as st
from openai import OpenAI
from linguabridge.service import LANGUAGES, Result, WorkflowError, demo_result, transcribe, translate

st.set_page_config(page_title="LinguaBridge AI", page_icon="🌐", layout="wide")
st.caption("LINGUABRIDGE AI  /  SPEECH → UNDERSTANDING")
st.title("Speak freely. Connect across languages.")
st.write("Record or upload audio, review the transcript, and translate it into your chosen language.")
mode = st.sidebar.radio("Workspace", ["Demo", "Live API"])
st.sidebar.caption("Demo uses a fixed sample. Live mode sends your recording and text to OpenAI.")
st.sidebar.markdown("**12 target languages**\n\nAudio stays in session memory. Export only what you choose.")
source = st.selectbox("Source language", ["Auto detect", *LANGUAGES])
target = st.selectbox("Translate into", list(LANGUAGES), index=1)
file = None
consent = False
if mode == "Live API":
    input_method = st.radio("Audio source", ["Upload a file", "Record with microphone"], horizontal=True)
    if input_method == "Upload a file":
        file = st.file_uploader("Audio (up to 24 MiB)", type=["wav", "mp3", "m4a", "mp4", "mpeg", "mpga", "webm"])
    else:
        file = st.audio_input("Record audio", sample_rate=16000)
    if file:
        st.audio(file)
    consent = st.checkbox("I have permission to process this audio and agree to send it and its transcript to OpenAI.")
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("Live mode needs OPENAI_API_KEY configured on the server. No key is needed for Demo.")
else:
    st.info("Sample workspace: the demo shows a fixed English transcript and prepared translations. No audio is processed.")

data = file.getvalue() if file else b""
fingerprint = (mode, source, target, hashlib.sha256(data).hexdigest())
if st.session_state.get("fingerprint") != fingerprint:
    st.session_state.fingerprint = fingerprint
    st.session_state.pop("transcript", None)
    st.session_state.pop("result", None)

if st.button("Load sample" if mode == "Demo" else "Transcribe audio", type="primary",
             disabled=mode == "Live API" and (not file or not consent or not os.getenv("OPENAI_API_KEY"))):
    st.session_state.pop("result", None)
    try:
        if mode == "Demo":
            st.session_state.result = demo_result(target)
            st.session_state.transcript = st.session_state.result.transcript
        else:
            with st.spinner("Transcribing audio…"):
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=60.0, max_retries=1)
                st.session_state.transcript = transcribe(client, file.name, data, source,
                                                        os.getenv("OPENAI_TRANSCRIPTION_MODEL", "whisper-1"))
    except WorkflowError as exc:
        st.error(str(exc))
    except Exception:
        st.error("The client could not start. Check the server's API configuration.")

if "transcript" in st.session_state:
    left, right = st.columns(2)
    with left:
        st.subheader("01 / Transcript")
        st.write(st.session_state.transcript)
        st.download_button("Download transcript", st.session_state.transcript, "transcript.txt", "text/plain")
    if mode == "Live API" and st.button("Translate transcript", disabled=not consent):
        st.session_state.pop("result", None)
        try:
            with st.spinner("Translating…"):
                client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], timeout=60.0, max_retries=1)
                translated = translate(client, st.session_state.transcript, target,
                                       os.getenv("OPENAI_TRANSLATION_MODEL", "gpt-4.1-mini"))
                st.session_state.result = Result(st.session_state.transcript, translated, source, target)
        except WorkflowError as exc:
            st.error(str(exc))
        except Exception:
            st.error("The client could not start. Check the server's API configuration.")
    if "result" in st.session_state:
        result = st.session_state.result
        with right:
            st.subheader(f"02 / {target}")
            st.write(result.translation)
            st.download_button("Download translation", result.translation, "translation.txt", "text/plain")
            st.download_button("Export JSON", result.to_json(), "linguabridge-result.json", "application/json")

if st.sidebar.button("Clear session results"):
    st.session_state.pop("transcript", None)
    st.session_state.pop("result", None)
    st.rerun()
st.divider()
st.caption("AI output can contain errors. Review before sharing. This version processes completed recordings, not real-time streams.")
