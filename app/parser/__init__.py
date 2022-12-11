from collections import namedtuple


__address_fields = ("ip_addr", "port", "domain_name",)
class Address(namedtuple(
    "Address",
    __address_fields,
    defaults=(None,) * len(__address_fields)
)):
    __slots__ = ()

SOCKET_CONN_TTL = 1
