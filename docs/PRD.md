A free, offline-first desktop dictation assistant that turns any microphone into a live “type-as-you-speak” engine, driven by Whisper and packaged in a lightweight tray app.

1 What it does
Feature	Highlights
Real-time STT	Streams audio through faster-whisper (CT2) for sub-second latency.
Global hot-key capture	Hold a configurable combo (default F12 or Ctrl + Shift) → recording, release → paste transcription.
Clipboard injector	Uses pyperclip to paste straight into the active text field—works in any app.
Tray & Headless modes	• Minimal RAM (<150 MB base).
• Tray icon for start/stop, settings window optional.
• Headless launch for power-users / scripting.
Model & mic auto-detect	Picks first working input device; users can pin a preferred mic & model size (tiny→large).
Robust audio pipeline	Ring-buffer, optional VAD (WebRTC/Silero), automatic stream re-open on -9999 errors.
Config persistence	Simple config.ini (or Pydantic JSON) for theme, hot-key, auto-launch, minimise-behaviour.
Cross-platform	Runs on Windows, macOS, most Linux distros; only Python ≥ 3.10 + pip install -r requirements.txt.
Fully offline	After 1st-run model download, no data leaves the machine.

2 Why it’s useful
Writers & coders speed-draft without SaaS fees (Dragon, Otter).

Accessibility for RSI sufferers or people who can’t afford proprietary voice software.

Privacy-critical roles—journalists, lawyers—keep audio local.

Hobby devs get a clean reference implementation of Whisper + Tkinter/pystray integration.

3 Technology stack
Core : Python 3.10+, faster-whisper, pyaudio, pynput, pyperclip.

GUI : Tkinter + ttkbootstrap (optional), pystray for system-tray.

Testing : pytest, ruff, black.

Packaging : pyinstaller for one-file EXE/AppImage when ready.

4 Road-map snapshot
Pre-flight headless build – proven (microphone, FW model, multiprocess, recorder).

Stable tray app – hot-key fix, auto-mic, retry on OSErrors.

Full desktop GUI (optional) – status badge, transcript pane, settings.

Quality passes – unit + smoke tests, CI green.

v0.1 release – one PR, binaries for Win/macOS, MIT licence.

5 Success criteria
Launches in <2 s post-model-ready.

Hot-key toggles reliably; no residual listeners after exit.

No -9999 PyAudio errors across common hardware.

All unit tests & manual smoke tests pass.

Users can dictate a paragraph into Word/VS Code without touching the mouse.