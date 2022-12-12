from abc import ABC, abstractmethod
import logging
from queue import Queue
from threading import Event, Thread
import time

logging.getLogger(__name__)


class BaseWorkerQueue(ABC):
    def __init__(
        self,
        maxsize: int = 0
    ):
        self._queue = Queue(maxsize=maxsize)
        self._paused = False
        self._started = False
        self._stop_event = Event()
        self._work_thread = None

    def has_started(self) -> bool:
        return self._started

    def has_stopped(self) -> bool:
        return self._stop_event.is_set()

    def is_paused(self) -> bool:
        return self._paused

    def put(self, item):
        self._queue.put(item)

    def put_nowait(self, item):
        self._queue.put_nowait(item)

    def pause(self):
        self._paused = True

    def unpause(self):
        self._paused = False

    def start(self):
        assert not self.has_started()
        event = Event()
        self._work_thread = Thread(target=self._start_impl, args=(event,), daemon=True)
        self._work_thread.start()
        # wait for thread start
        event.wait()
        self._started = True
        logging.debug(
            "Queue worker %s has successfully started",
            self.__class__.__name__
        )

    def stop(self):
        assert self.has_started()
        self._stop_event.set()
        self._work_thread.join()

    @abstractmethod
    def process_item(self, item):
        pass

    def _start_impl(self, event: Event):
        try:
            event.set()
            self.__work_loop()
        except Exception as exc:
            logging.error("Exception passed from work_loop: %s", str(exc))
            raise exc
        finally:
            self._finalize()

    def _finalize(self):
        pass

    def __work_loop(self):
        while True:
            if self._stop_event.is_set():
                return
            if self.is_paused():
                time.sleep(0.1)
            else:
                item = self._queue.get()
                start_time = time.monotonic()
                logging.debug(
                    "Starting work loop iteration in %s",
                    self.__class__.__name__
                )
                self.process_item(item)
                logging.debug(
                    "Ended work loop iteration in %s, elapsed %ss",
                    self.__class__.__name__,
                    time.monotonic() - start_time
                )
