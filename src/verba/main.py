from threading import Thread

from verba.audio.recorder import AudioRecorder
from verba.core.assistant import PlaceholderSpeechTranscriber, VerbaAssistant
from verba.core.types import AssistantTurn, RecorderDiagnostics
from verba.frontend.tkinter.window import TkinterWindow
from verba.trigger.manual_trigger import ManualTrigger


def main() -> None:
	recorder = AudioRecorder()
	assistant = VerbaAssistant(transcriber=PlaceholderSpeechTranscriber())
	trigger_recording = ManualTrigger()
	window = TkinterWindow(on_manual_trigger=trigger_recording.fire)

	def format_diagnostics(diagnostics: RecorderDiagnostics) -> str:
		return (
			f"state={diagnostics.state} | elapsed={diagnostics.elapsed_seconds:.2f}s | "
			f"captured={diagnostics.captured_seconds:.2f}s\n"
			f"rms={diagnostics.current_rms:.6f} | active={diagnostics.active_threshold:.6f} | "
			f"noise_floor={diagnostics.noise_floor:.6f}\n"
			f"start={diagnostics.start_threshold:.6f} | continue={diagnostics.continue_threshold:.6f}\n"
			f"silent_time={diagnostics.silent_seconds:.2f}s | "
			f"speech_started={diagnostics.speech_started} | overflows={diagnostics.overflow_count}"
			f"{f' | stop={diagnostics.stop_reason}' if diagnostics.stop_reason else ''}"
		)

	def publish_diagnostics(diagnostics: RecorderDiagnostics) -> None:
		window.call_soon(
			lambda diagnostics=diagnostics: window.show_diagnostics(format_diagnostics(diagnostics))
		)

	def record_in_background() -> None:
		try:
			recording = recorder.record(on_diagnostics=publish_diagnostics)
			turn = assistant.handle_recording(recording)
			window.call_soon(lambda: on_recording_finished(turn))
		except Exception as error:
			window.call_soon(lambda error=error: on_recording_failed(error))

	def on_recording_finished(turn: AssistantTurn) -> None:
		window.set_status("idle")
		window.show_transcript(turn.transcript)
		window.show_response(turn.response)

	def on_recording_failed(e: Exception) -> None:
		window.set_status("idle")
		window.show_transcript(f"Recording failed: {e}")
		window.show_response("")
		window.show_diagnostics("Recorder failed before diagnostics could complete.")

	def handle_trigger_recording() -> None:
		window.set_status("recording")
		window.show_transcript("Listening...")
		window.show_response("")
		window.show_diagnostics("Recorder starting. Calibrating room noise...")
		Thread(target=record_in_background, daemon=True).start()

	trigger_recording.start(handle_trigger_recording)
	window.run()