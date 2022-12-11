from app.common.utils.queue_worker import BaseWorkerQueue
from app.parser.base import BaseIPScanner


class ScannerQueue(BaseWorkerQueue):
    _instance: BaseWorkerQueue = None

    def process_item(self, item: BaseIPScanner):
        item.scan()

    @classmethod
    def get_instance(cls) -> BaseWorkerQueue:
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
