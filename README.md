# LinguaBridge AI

**A speech-first workspace for transcription and multilingual translation.**

Upload a recording or capture microphone audio, transcribe it with OpenAI, then translate the transcript into one of 12 languages. The Streamlit interface separates the two requests so you can review speech recognition before spending another API call on translation.

## Implemented

- Uploads and browser microphone capture for completed recordings.
- Source-language hints or automatic detection; 12 target-language choices.
- OpenAI Audio Transcriptions and Responses API integration through an injectable Python service.
- Input validation (supported formats, non-empty audio, 24 MiB limit), bounded requests, and safe error messages for access, rate-limit, input, and connection failures.
- Transcript, translation, and Unicode JSON downloads.
- Consent before sending audio/text to the API; session-only results and a clear-results control.
- A clearly labeled, credential-free demo with fixed sample translations.
- Automated service and Streamlit interface tests; GitHub Actions configuration.

## Quick start

Requires Python 3.12+. From this repository:

```bash
python -m venv .venv
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
streamlit run app.py
```

Open the localhost URL printed by Streamlit. Choose **Demo**, a target language, and **Load sample**. Demo does not transcribe your audio.

### Live API setup

Supply `OPENAI_API_KEY` using your terminal's environment or your hosting service's secret manager. Do not type it into source code, commit it, paste it into issues, or expose it in a screenshot. `.env.example` documents variable names; this app does not auto-load `.env` files. Hosted Streamlit secrets are also supported.

Optional server variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `OPENAI_API_KEY` | None | Server-side provider credential |
| `OPENAI_TRANSCRIPTION_MODEL` | `whisper-1` | File transcription model |
| `OPENAI_TRANSLATION_MODEL` | `gpt-4.1-mini` | Text translation model |

Choose **Live API**, upload or record audio, select languages, and give processing consent. Click **Transcribe audio**, review the transcript, then **Translate transcript**. Your account needs access to the selected models and sufficient billing quota. Calls can incur charges.

## Test

```bash
python -m pytest -q
```

Tests use mocked provider responses and Streamlit AppTest; they do not require a key or incur charges. Cases include empty/oversized/unsupported uploads, language hints, empty speech, incomplete translation, sanitized errors, demo exports, disabled live mode without credentials, and result invalidation when inputs change.

## Architecture

`app.py` owns explicit user actions and session state. `linguabridge/service.py` owns validation, result serialization, and provider calls. Uploaded bytes are passed from memory with an anonymized filename. Provider error bodies never reach the interface. Responses API storage is disabled (`store=False`); provider retention rules still apply. The application makes no claim of zero provider retention.

## Verification and limits

The local service/interface test suite passed. **Live transcription and translation have not been exercised against a real account** because no API key was supplied. Browser microphone permissions require localhost or HTTPS. This version has no streaming transcription, speaker diarization, audio chunking, persisted history, or authentication. Extension/size validation is not a full audio decoder; corrupt or silent files can be rejected by the provider. AI transcription/translation may be inaccurate. Use short recordings and review all output.

Dependencies are pinned to the versions used locally. CI is configured but has not run on GitHub while repository access is unavailable.

## Official references

- [OpenAI file transcription](https://developers.openai.com/api/docs/guides/speech-to-text)
- [OpenAI text generation](https://developers.openai.com/api/docs/guides/text)
- [Streamlit audio input](https://docs.streamlit.io/develop/api-reference/widgets/st.audio_input)


## Deploy on Streamlit Community Cloud

Connect your GitHub account at https://share.streamlit.io, choose this repository and branch main, and set the entrypoint to app.py. In Advanced settings, store OPENAI_API_KEY in the Secrets editor; never commit secrets.toml. The app reads server environment variables first and hosted Streamlit secrets second. Optional transcription and translation model names use the same settings. Deploy without a key to test Demo first.

A Dockerfile is supplied for Python container hosts. Set credentials through the host secret manager, serve HTTPS, and forward the service's port 8501. The image runs as a non-root user and checks Streamlit health. Docker image build was not verified because Docker is unavailable in the authoring environment. The application has not yet been deployed to a Python host or tested with a live API key.
