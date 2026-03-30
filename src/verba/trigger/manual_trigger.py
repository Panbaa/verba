from collections.abc import Callable


class ManualTrigger:
	def __init__(self) -> None:
		self._callback: Callable[[], None] | None = None

	def start(self, on_trigger: Callable[[], None]) -> None:
		self._callback = on_trigger

	def stop(self) -> None:
		self._callback = None

	def fire(self) -> None:
		if self._callback is not None:
			self._callback()
