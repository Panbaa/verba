# Plan: Local Commercial-Safe MVP
Recommended stack for the first pass:

1. Python for the app shell and orchestration.
2. sounddevice for local audio I/O.
3. faster-whisper for local STT.
4. `LLMClient` as the stable abstraction, with llama.cpp via llama-cpp-python as the first local backend and room for later external endpoint backends.
5. Tkinter for the popup UI.
6. A local TTS engine only after both the engine and the exact voice/model asset are verified as commercially usable under a permissive license.

## Next Days
1. ~~Day 1: create a license whitelist before coding anything substantial. Audit every package, model, and voice asset you might use, because the TTS voice/model license is the easiest place to accidentally break your commercial-use requirement.~~
2. ~~Day 1: lock the MVP stack and define the interfaces for recorder, STT, LLM, TTS, UI, and trigger source.~~
3. Day 1: Implement the first empty startable application with a button to trigger audio capture.
4. Day 2: implement local audio capture and playback, with one fixed audio format such as mono 16 kHz. Verify mic and speaker behavior on your Linux machine.
5. Day 2 to Day 3: integrate faster-whisper and get speech-to-text working locally with a stable default configuration. Measure latency on a short utterance before tuning.
6. Day 3 to Day 4: integrate the first local LLM backend via `LLMClient`. Start with `LlamaCppLLM`, use a model whose license is explicit and permissive, and load it from a local file path. Keep the design ready for later endpoint-based backends, but do not make the MVP depend on an external service.
7. Day 4: integrate TTS as a hard requirement for MVP, but only after the exact engine and voice asset pass the license check. This is the main gating item in your plan.
8. Day 4 to Day 5: add to the popup UI just four states: recording, transcribing, thinking, speaking. Show transcript and response text.
9. Day 5 to Day 6: add the global hotkey behind a trigger abstraction. Because your Linux session is still unknown, keep a manual fallback path available even after hotkey support is added.
10. Day 6: harden the flow with cancellation, repeated-trigger protection, model-missing errors, invalid-audio-device handling, and clear local error messages in the popup.
11. Day 7: run end-to-end validation with networking disabled after install, confirm the app still works fully offline, and freeze MVP scope.

## Key Decisions
1. Do not start with the hotkey. Linux hotkeys are the most environment-specific part of the product, so they should come after the core voice pipeline already works.
2. Avoid Qt for the first MVP because you asked for MIT/Apache/BSD-only dependencies.
3. Treat model files and TTS voice assets as first-class dependencies, not just the Python packages around them.
4. Keep the MVP to one local conversation flow only. No memory, plugins, multi-agent routing, or cross-platform work yet.

## Main Risk
The biggest unresolved issue is TTS licensing, not STT or the LLM runtime. If you want the first MVP to stay commercially safe, the exact local TTS voice/model asset must be chosen and verified on day 1.

I saved the detailed version into session memory so it can be refined. If you want, the next step is either:

1. refine this plan into a strict 5-day schedule, or
2. turn it into a dependency shortlist with exact MIT/Apache/BSD candidates for STT, LLM, TTS, and hotkeys.
