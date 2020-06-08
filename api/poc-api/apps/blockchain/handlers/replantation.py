import logging

from typing import TYPE_CHECKING

from protos.entity_pb2 import Replantation
from protos.enums import Namespaces, Tbl
from apps.blockchain.handlers._base import HandlerBase

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class PackageHandler(HandlerBase):
    prefix = Namespaces.get_prefix(Namespaces.REPLANTATION)

    @staticmethod
    def process(changes: "StateChange"):
        LOG.info(f"Process changes with `ReplantationHandler`: {changes.address}")
        replantation = Replantation()
        replantation.ParseFromString(changes.value)
        LOG.debug(f"Package: {replantation.id}")
