import asyncio
import threading
from concurrent.futures import Future
from typing import Callable, Optional

from gi.repository import GLib


class AsyncBridge:
    _instance: Optional["AsyncBridge"] = None
    _instance_lock: threading.Lock = threading.Lock()

    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    @classmethod
    def get(cls) -> "AsyncBridge":
        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def _run_loop(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    def run(self, coro) -> Future:
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def idle_add(self, callback: Callable, *args):
        GLib.idle_add(callback, *args)

    def stop(self):
        self._loop.call_soon_threadsafe(self._loop.stop)
