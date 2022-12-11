import concurrent.futures
from ipaddress import IPv4Address
import logging

from app.common.models.address import Address, IPRange
from app.common.utils.network import SyncSingleSession, ip_available
from app.parser.base import BaseIPScanner
from app.parser.certificate_getter import SSLCerificateGetter
from app.parser.scanners import SSLSocketScanner
from app.parser.settings import Settings

logging.getLogger(__name__)


class IPScanner(BaseIPScanner):
    _default_ports = [
        25,
        53,
        80,
        161,
        162,
        443,
        7102,
        7104,
        7105,
        8080,
    ]

    def __init__(self, ip_range: IPRange, query_id: int):
        self._query_id = query_id
        super().__init__(ip_range)

    def ports(self, ip_address: IPv4Address) -> list[int]:
        if not ip_available(ip_address):
            return []
        return self._default_ports

    def scan(self):
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=Settings.get_settings().workers_count
        ) as executor:
            futures_list = []
            addr = self._ip_range.start
            while addr != self._ip_range.end:
                futures_list.append(executor.submit(self._scan_one_address, addr))
                addr += 1

            for future in concurrent.futures.as_completed(futures_list):
                try:
                    future.result()
                except Exception as exc:
                    logging.critical("Unhandled exception: %s", str(exc))

    def _scan_one_address(self, addr: IPv4Address):
        ports = self.ports(addr)
        for port in ports:
            scanner = SSLSocketScanner(
                [SSLCerificateGetter(query_id=self._query_id)],
                Address(str(addr), port)
            )
            if scanner.scan():
                # send result to analyzer
                resp = SyncSingleSession.request(
                    "POST",
                    f"{Settings.get_settings().get_analyzer_addr()}/raw_cert",
                    data=scanner.get_certificate().cerificate_data.to_json(),
                )
                if not resp.ok:
                    logging.error(
                        "Failed to send certificate (query_id %d) to analyzer",
                        self._query_id
                    )
