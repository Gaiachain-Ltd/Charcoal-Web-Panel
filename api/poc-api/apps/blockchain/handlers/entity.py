import logging

from typing import TYPE_CHECKING

from protos.entity_pb2 import Entity
from protos.enums import Namespaces
from apps.blockchain.handlers._base import HandlerBase

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class EntityHandler(HandlerBase):
    prefix = Namespaces.get_prefix(Namespaces.ENTITY)

    @staticmethod
    def process(changes: "StateChange"):
        LOG.info(f"Process changes with `EntityHandler`: {changes.address}")
        entity = Entity()
        entity.ParseFromString(changes.value)
        LOG.debug(f"Entity: {entity.id} ({entity.commodity_type})")
