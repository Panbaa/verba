from tkinter import StringVar, Tk
from tkinter import ttk
from typing import Callable


class TkinterWindow:
	def __init__(self, on_manual_trigger: Callable[[], None]) -> None:
		self._on_manual_trigger = on_manual_trigger
		self._root = Tk()
		self._root.title("Verba")
		self._root.geometry("420x420")

		self._status = StringVar(value="idle")
		self._transcript = StringVar(value="Waiting for input...")
		self._response = StringVar(value="No response yet.")

		container = ttk.Frame(self._root, padding=16)
		container.grid(sticky="nsew")

		self._root.columnconfigure(0, weight=1)
		self._root.rowconfigure(0, weight=1)
		container.columnconfigure(0, weight=1)

		ttk.Label(container, text="Verba", font=("TkDefaultFont", 14, "bold")).grid(
			row=0, column=0, sticky="w"
		)
		ttk.Label(container, textvariable=self._status).grid(row=1, column=0, sticky="w", pady=(6, 12))

		ttk.Button(container, text="Record", command=self._handle_manual_trigger).grid(
			row=2, column=0, sticky="ew"
		)
		ttk.Button(container, text="Quit", command=self._root.destroy).grid(
			row=3, column=0, sticky="ew", pady=(8, 0)
		)

		ttk.Label(container, text="Transcript").grid(row=4, column=0, sticky="w", pady=(16, 0))
		ttk.Label(container, textvariable=self._transcript, wraplength=360).grid(
			row=5, column=0, sticky="w", pady=(4, 0)
		)

		ttk.Label(container, text="Response").grid(row=6, column=0, sticky="w", pady=(12, 0))
		ttk.Label(container, textvariable=self._response, wraplength=360).grid(
			row=7, column=0, sticky="w", pady=(4, 0)
		)

	def _handle_manual_trigger(self) -> None:
		self._on_manual_trigger()

	def set_status(self, status: str) -> None:
		self._status.set(f"Status: {status}")

	def show_transcript(self, transcript: str) -> None:
		self._transcript.set(transcript)

	def show_response(self, response: str) -> None:
		self._response.set(response)

	def run(self) -> None:
		self._root.mainloop()