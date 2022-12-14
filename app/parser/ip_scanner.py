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
    # arrange by popularity, according to Towards a Complete View of the SSL/TLS Service Ports in the Wild
    # 10.1007/978-3-030-41114-5 p. 562
    _default_ports = [
        443,  # should be first, as the most default
        80,
        8443,
        3389,
        993,
        8080,
        465,
        5223,
        2083,
        3128,
        995,
        21,
        22,
        25,
        53,
        110,
        161,
        162,
        3306,
        7102,
        7104,
        7105,
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
                logging.debug("Scanning address %s", str(addr))
                futures_list.append(executor.submit(self._scan_one_address, addr))
                addr += 1

            for future in concurrent.futures.as_completed(futures_list):
                try:
                    future.result()
                except Exception as exc:
                    logging.critical("Unhandled exception: %s", str(exc), exc_info=True)

    def _scan_one_address(self, addr: IPv4Address):
        ports = self.ports(addr)
        for port in ports:
            scanner = SSLSocketScanner(
                [SSLCerificateGetter(query_id=self._query_id)],
                Address(str(addr), port)
            )
            logging.debug("Scanning (IP %s, port %d)", str(addr), port)
            if scanner.scan():
                # send result to analyzer
                logging.debug("Sending certificate from (IP %s, port %d)", str(addr), port)
                resp = SyncSingleSession.request(
                    "POST",
                    f"{Settings.get_settings().get_analyzer_addr()}/raw_cert",
                    json=scanner.get_certificate().cerificate_data.to_json(),
                )
                if not resp.ok:
                    logging.error(
                        "Failed to send certificate (query_id %d) to analyzer",
                        self._query_id
                    )
