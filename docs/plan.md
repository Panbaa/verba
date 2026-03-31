# 🧠 Voice Assistant App – Plan.md

## 1. Vision

A **local-first, configurable voice assistant** that:

* Runs natively on the user's system (starting with Linux)
* Can be triggered via a global keyboard shortcut
* Uses interchangeable LLMs (local-first, model-agnostic design)
* Supports different assistant roles (coding partner, teacher, etc.)

---

## 2. Core Principles

* 🔒 Local-first (privacy-focused)
* ⚡ Fast iteration (prototype first, refine later)
* 🧩 Modular architecture (replace components easily)
* 🔌 Model-agnostic (LLMs are interchangeable)
* 🖥️ Cross-platform future (Linux → Windows → macOS → mobile → web)

---

## 3. MVP Scope (v1)

### ✅ Included

* Global hotkey trigger (e.g. Ctrl + H)
* Push-to-talk voice recording
* Speech-to-text (local)
* LLM interaction (initially via dummy abstraction)
* Text-to-speech (local)
* Popup UI (minimal overlay window)

### ❌ Excluded (for now)

* Multi-agent routing
* Plugin system
* Mobile apps
* Complex memory/context system
* Multimodal inputs (images, files)

---

## 4. User Flow

1. User presses global shortcut
2. UI popup appears
3. Recording starts
4. User speaks
5. Audio → text (STT)
6. Text → LLM
7. Response → text
8. Text → speech (TTS)
9. Audio playback + UI displays response

---

## 5. High-Level Architecture

### Core Components

* Hotkey Listener
* Audio Recorder
* Speech-to-Text (STT)
* LLM Client (abstracted)
* Text-to-Speech (TTS)
* Audio Playback
* UI Overlay
* Assistant Controller (orchestrator)

---

## 6. Architecture Design (Modular)

### 6.1 Assistant Orchestrator

Responsible for coordinating the pipeline:

```
User Input → STT → Router → LLM → TTS → Output
```

---

### 6.2 LLM Abstraction Layer

Design early for flexibility:

```python
class LLMClient:
    def generate(self, prompt: str) -> str:
        raise NotImplementedError
```

Initial implementation:

* LlamaCppLLM (local-first backend using llama.cpp)

Future:

* OllamaLLM
* OpenAI-compatible endpoint backend
* Private self-hosted endpoint backend

---

### 6.3 Router (Future-ready)

Even if unused initially:

```python
class Router:
    def route(self, text: str) -> str:
        return self.default_agent.respond(text)
```

The router should operate at the `LLMClient` level so the assistant can later switch between local and external backends without changing orchestrator logic.

---

### 6.4 STT Module

Initial:

* Local faster-whisper as the default MVP STT backend

Why this choice:

* Local-first and commercially plausible with license review of both code and model assets
* Easier to integrate into the current Python service architecture than whisper.cpp
* Good speed and accuracy tradeoff for the MVP

Planned next step:

* Implement a `SpeechTranscriber` service backed by faster-whisper
* Keep STT swappable behind the existing protocol so a different local backend or a custom STT can be added later without redesigning the app

---

### 6.5 TTS Module

Options:

* pyttsx3 (simple, offline)
* Coqui TTS (higher quality, still local)

---

### 6.6 UI Layer

Requirements:

* Small popup window
* Shows:

  * Recording state
  * Transcribed text
  * Response text

Tech options:

* PyQt (recommended)
* Tkinter (simpler, less flexible)

---

### 6.7 Hotkey System

* Global keyboard listener
* Triggers assistant activation

---

## 7. Tech Stack (Initial)

* Language: Python
* UI: Tkinter
* Audio: sounddevice
* STT: faster-whisper
* TTS: local engine to be finalized after license review of engine and voice assets
* LLM abstraction: `LLMClient`
* First LLM backend: llama.cpp via llama-cpp-python
* Future LLM backends: Ollama or private/self-hosted API endpoints behind the same `LLMClient` interface

---

## 8. Development Phases

### Phase 1: Core Logic (Text-only)

* Implement LLM interface
* Implement `LLMClient`
* Start with `LlamaCppLLM`
* CLI interaction

---

### Phase 2: Voice Input

* Record audio
* Convert speech → text with faster-whisper
* Expose transcription progress and failure states in the UI

---

### Phase 3: Voice Output

* Convert response → speech
* Play audio

---

### Phase 4: UI Integration

* Build popup window
* Display transcription + response

---

### Phase 5: Hotkey Trigger

* Global shortcut activation

---

### Phase 6: Refinement

* Improve latency
* Add cancel/interruption
* Improve UX feedback

---

## 9. File/Folder Structure (Proposed)

```
assistant/
├── core/
│   ├── assistant.py
│   ├── router.py
│
├── llm/
│   ├── base.py
│   ├── dummy.py
│
├── audio/
│   ├── recorder.py
│   ├── player.py
│
├── stt/
│   ├── whisper.py
│
├── tts/
│   ├── tts_engine.py
│
├── ui/
│   ├── window.py
│
├── input/
│   ├── hotkey.py
│
├── main.py
```

---

## 10. Key Challenges

### Latency

* STT + LLM + TTS must be fast

### Current Direction

* Recording and silence detection are implemented
* The next implementation session should focus on integrating faster-whisper into the `SpeechTranscriber` boundary
* Do not couple the UI directly to faster-whisper specific code; keep the backend behind the protocol layer
* Consider streaming later

### Linux System Integration

* Global hotkeys may differ (X11 vs Wayland)
* Audio device handling

### Audio UX

* Feedback sounds
* Clear start/stop states

---

## 11. Future Roadmap

* Multi-agent routing
* Context awareness (active app, coding mode, etc.)
* Plugin system
* Cross-platform builds
* Mobile companion app
* Advanced memory system

---

## 12. Guiding Philosophy

> Build a thin, working vertical slice first.
> Then iterate by replacing internals—not redesigning the system.

---

## 13. Next Steps

1. Create project structure
2. Implement DummyLLM
3. Build assistant orchestrator
4. Add CLI loop
5. Incrementally add voice + UI

---
