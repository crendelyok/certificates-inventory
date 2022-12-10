# import ssl
#
# from app.parser.base import Address, BaseCertificateGetter
#
#
# class SSLChecker(BaseProtocolChecker):
#     async def check(self, addr: Address, **kwargs) -> str | None:
#
#
#
#
#         # TODO(slynkodenis): rewrite with async usage
#         try:
#             return ssl.get_server_certificate(addr, timeout=kwargs.get("timeout", 10))
#         except (ConnectionRefusedError, TimeoutError,):
#             return None
