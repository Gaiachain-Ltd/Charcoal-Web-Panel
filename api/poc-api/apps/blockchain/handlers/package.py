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
        # r.table(Tbl.ENTITIES).insert(
        #     {
        #         "id": entity.id,
        #         "ref": changes.address,
        #         "generator_public_key": entity.generator_public_key,
        #         "generation_timestamp": entity.generation_timestamp,
        #         "assignment_timestamp": entity.assignment_timestamp or None,
        #         "commodity_type": Entity.CommodityType.Name(entity.commodity_type),
        #         "entity_batch_id": entity.entity_batch_id,
        #         "finished_timestamp": entity.finished_timestamp or None,
        #         "is_initialized": bool(entity.entity_batch_id),
        #         "is_finished": entity.finished_timestamp > 0,
        #     },
        #     conflict="update",
        # ).run()
