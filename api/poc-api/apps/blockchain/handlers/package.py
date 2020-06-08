import logging

from typing import TYPE_CHECKING

from protos.entity_pb2 import Package
from protos.enums import Namespaces, Tbl
from apps.blockchain.handlers._base import HandlerBase

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class PackageHandler(HandlerBase):
    prefix = Namespaces.get_prefix(Namespaces.PACKAGE)

    @staticmethod
    def process(changes: "StateChange"):
        LOG.info(f"Process changes with `PackageHandler`: {changes.address}")
        package = Package()
        package.ParseFromString(changes.value)
        LOG.debug(f"Package: {package.id} ({package.type})")
