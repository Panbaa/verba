from verba.frontend.tkinter.window import TkinterWindow
from verba.trigger.manual_trigger import ManualTrigger
from verba.audio.recorder import AudioRecorder
from threading import Thread

recorder = AudioRecorder()

def main() -> None: 
	trigger_recording = ManualTrigger()
	
	def record_in_background() -> None:
		try:
			wav_bytes = recorder.record_wav()
			window._root.after(0, lambda: on_recording_finished(wav_bytes))
		except Exception as error:
			window._root.after(0, lambda error=error: on_recording_failed(error))

	def on_recording_finished(wav_bytes: bytes) -> None:
		window.set_status("idle")
		if len(wav_bytes) <= 44:
			window.show_transcript("No speech detected.")
			window.show_response("")
			return

		window.show_transcript("Recorded audio captured.")
		window.show_response(f"Captured audio length: {len(wav_bytes)} bytes.")

	def on_recording_failed(e: Exception) -> None:
		window.set_status("idle")
		window.show_transcript(f"Recording failed: {e}")
		window.show_response("")

	def handle_trigger_recording() -> None:
		window.set_status("recording")
		window.show_transcript("Listening...")
		Thread(target=record_in_background, daemon=True).start()

	window = TkinterWindow(on_manual_trigger=trigger_recording.fire)
	trigger_recording.start(handle_trigger_recording)
	window.run()