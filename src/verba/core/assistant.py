from verba.core.protocols import SpeechTranscriber
from verba.core.types import AssistantTurn, RecordingResult


class PlaceholderSpeechTranscriber:
	def transcribe(self, recording: RecordingResult) -> str:
		if not recording.speech_detected:
			return ""

		return "Speech captured successfully. Connect a real STT backend next."


class VerbaAssistant:
	def __init__(self, transcriber: SpeechTranscriber) -> None:
		self._transcriber = transcriber

	def handle_recording(self, recording: RecordingResult) -> AssistantTurn:
		transcript = self._transcriber.transcribe(recording)
		if not recording.speech_detected:
			return AssistantTurn(
				transcript="No speech detected.",
				response=(
					f"Stopped: {recording.stop_reason} | elapsed: "
					f"{recording.diagnostics.elapsed_seconds:.2f}s"
				),
				recording=recording,
			)

		response = (
			f"Duration: {recording.duration_seconds:.2f}s | bytes: {recording.byte_length} | "
			f"peak: {recording.peak_level:.4f} | stopped: {recording.stop_reason}"
		)
		return AssistantTurn(
			transcript=transcript,
			response=response,
			recording=recording,
		)
