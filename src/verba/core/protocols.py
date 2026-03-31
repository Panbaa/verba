from typing import Protocol

from verba.core.types import AssistantTurn, RecordingResult


class SpeechTranscriber(Protocol):
	def transcribe(self, recording: RecordingResult) -> str:
		...


class Assistant(Protocol):
	def handle_recording(self, recording: RecordingResult) -> AssistantTurn:
		...
