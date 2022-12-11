from app.common.utils.queue_worker import BaseWorkerQueue
from app.parser.base import BaseIPScanner


class ScannerQueue(BaseWorkerQueue):
    _instance: BaseWorkerQueue = None

    def process_item(self, item: BaseIPScanner):
        item.scan()

    @classmethod
    def init(cls):
        assert cls._instance is None
        cls._instance = cls()

    @classmethod
    def get_instance(cls) -> BaseWorkerQueue:
        return cls._instance
