"""Interrupt handler for cancelling running action sequences."""

import threading


class InterruptHandler:
    """Thread-safe interrupt flag for cancelling running action sequences."""

    def __init__(self):
        self._interrupted = threading.Event()

    def interrupt(self):
        """Set the interrupt flag."""
        self._interrupted.set()

    def clear(self):
        """Clear the interrupt flag."""
        self._interrupted.clear()

    def is_interrupted(self) -> bool:
        """Check if an interrupt has been requested."""
        return self._interrupted.is_set()

    def check(self):
        """Raise InterruptedError if interrupted."""
        if self._interrupted.is_set():
            raise InterruptedError("Execution cancelled by user")


INTERRUPT = InterruptHandler()
