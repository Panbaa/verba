from verba.frontend.tkinter.window import TkinterWindow
from verba.trigger.manual_trigger import ManualTrigger


def main() -> None: 
	trigger = ManualTrigger()

	def handle_trigger() -> None:
		window.set_status("recording")
		window.show_transcript("Manual trigger fired. Recorder not connected yet.")
		window.show_response("Next step: connect audio capture in the trigger callback.")

	window = TkinterWindow(on_manual_trigger=trigger.fire)
	trigger.start(handle_trigger)
	window.run()
