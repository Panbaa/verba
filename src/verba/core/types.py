from dataclasses import dataclass


@dataclass(slots=True)
class RecorderDiagnostics:
	state: str
	elapsed_seconds: float
	captured_seconds: float
	current_rms: float
	active_threshold: float
	start_threshold: float
	continue_threshold: float
	noise_floor: float
	silent_seconds: float
	speech_started: bool
	overflow_count: int
	stop_reason: str = ""


@dataclass(slots=True)
class RecordingResult:
	wav_bytes: bytes
	speech_detected: bool
	duration_seconds: float
	peak_level: float
	stop_reason: str
	diagnostics: RecorderDiagnostics

	@property
	def byte_length(self) -> int:
		return len(self.wav_bytes)


@dataclass(slots=True)
class AssistantTurn:
	transcript: str
	response: str
	recording: RecordingResult
