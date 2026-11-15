"""One scheduled check at a time. Disabled until the user turns it on."""
from __future__ import annotations

import threading

class Scheduler:
    def __init__(self, interval_s: int, job):
        if interval_s < 1:
            raise ValueError("interval must be positive")
        self.interval_s = interval_s
        self.job = job
        self._timer: threading.Timer | None = None
        self._running = False
        self._lock = threading.Lock()
        self.enabled = False

    def start(self) -> None:
        self.enabled = True
        self._arm()

    def stop(self) -> None:
        self.enabled = False
        if self._timer:
            self._timer.cancel()
            self._timer = None

    def _arm(self) -> None:
        if not self.enabled:
            return
        self._timer = threading.Timer(self.interval_s, self._fire)
        self._timer.daemon = True
        self._timer.start()

    def _fire(self) -> None:
        if not self._lock.acquire(blocking=False):
            self._arm()
            return
        self._running = True
        try:
            self.job()
        finally:
            self._running = False
            self._lock.release()
            self._arm()
