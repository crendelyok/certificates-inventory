import logging

from app.common.utils.queue_worker import BaseWorkerQueue
from app.parser.base import BaseIPScanner

logging.getLogger(__name__)


class ScannerQueue(BaseWorkerQueue):
    _instance: BaseWorkerQueue = None

    def process_item(self, item: BaseIPScanner):
        try:
            item.scan()
        except Exception as exc:
            logging.critical("Unhandled exception: %s", str(exc), exc_info=True)

    @classmethod
    def init(cls):
        assert cls._instance is None
        cls._instance = cls()

    @classmethod
    def get_instance(cls) -> BaseWorkerQueue:
        return cls._instance
