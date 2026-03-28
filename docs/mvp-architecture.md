# MVP Architecture

This document captures the locked MVP architecture decisions from step 2 of the workplan. It exists so the implementation details for the first MVP are stored in one place and can be referenced without scanning the full schedule.

## Locked MVP Stack

- Python 3.12+
- Local app architecture: plain Python package with interface-first module boundaries
- Audio I/O: sounddevice
- STT: faster-whisper
- LLM abstraction: `LLMClient`
- First LLM backend: `LlamaCppLLM` implemented with llama-cpp-python backed by llama.cpp
- Initial local LLM model target: an Apache-2.0 or MIT licensed GGUF model stored locally and loaded by path, not by remote API
- Future LLM backend path: add `OllamaLLM` or an OpenAI-compatible/private endpoint backend behind the same `LLMClient` interface
- UI: Tkinter
- Trigger source: manual trigger first, global hotkey second behind the same abstraction
- TTS: interface locked now, concrete backend only after the exact engine and voice asset pass the license whitelist

## Core Runtime Types

- `AudioChunk`: raw mono PCM audio plus sample rate metadata
- `Transcript`: transcribed text plus optional language metadata
- `LLMResponse`: response text plus optional generation metadata
- `SynthesisResult`: playable local audio plus sample rate metadata

## Minimal Interface Contracts

These are the minimum contracts every backend must satisfy so the orchestrator can swap implementations without changing application flow.

```python
from dataclasses import dataclass
from typing import Callable, Protocol


@dataclass
class AudioChunk:
    samples: object
    sample_rate: int


@dataclass
class Transcript:
    text: str
    language: str | None = None


@dataclass
class LLMResponse:
    text: str


@dataclass
class SynthesisResult:
    samples: object
    sample_rate: int


class Recorder(Protocol):
    def record(self, max_seconds: float, sample_rate: int = 16000) -> AudioChunk:
        ...


class SpeechToText(Protocol):
    def transcribe(self, audio: AudioChunk) -> Transcript:
        ...


class LLMClient(Protocol):
    def generate(self, prompt: str, system_prompt: str | None = None) -> LLMResponse:
        ...


class TextToSpeech(Protocol):
    def synthesize(self, text: str) -> SynthesisResult:
        ...


class AssistantUI(Protocol):
    def show_idle(self) -> None:
        ...

    def show_recording(self) -> None:
        ...

    def show_transcribing(self) -> None:
        ...

    def show_thinking(self) -> None:
        ...

    def show_speaking(self) -> None:
        ...

    def show_transcript(self, transcript: str) -> None:
        ...

    def show_response(self, response: str) -> None:
        ...

    def show_error(self, message: str) -> None:
        ...


class TriggerSource(Protocol):
    def start(self, on_trigger: Callable[[], None]) -> None:
        ...

    def stop(self) -> None:
        ...
```

## Orchestrator Ownership

The orchestrator is the only component allowed to coordinate a full assistant turn.

- Owns the single user turn from trigger to playback
- Updates UI state in this order: idle -> recording -> transcribing -> thinking -> speaking -> idle
- Prevents overlapping runs
- Keeps all backends swappable without changing orchestration logic
- Depends only on interfaces, not on backend-specific implementation details

## LLM Backend Rule

- The orchestrator only depends on `LLMClient`, never on llama.cpp, Ollama, or any specific endpoint protocol
- `LlamaCppLLM` is the first implementation for the MVP because it keeps inference fully local
- Later, a routed or configurable `LLMClient` can dispatch to local or external backends without changing the rest of the app

## Initial Implementation Rule

- Do not let UI, hotkey, STT, TTS, or model-specific code call each other directly
- All coordination goes through the orchestrator and the interfaces above
- Keep the first implementation minimal and local-first
- Add external endpoint support only as an additional `LLMClient` implementation, not as a redesign