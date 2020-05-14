import logging
from datetime import datetime

import time

import rethinkdb as r
from typing import TYPE_CHECKING

from protos.entity_pb2 import Entity, EntityBatch
from protos.enums import Namespaces, Tbl
from sync.handlers._base import HandlerBase

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class EntityBatchHandler(HandlerBase):
    prefix = Namespaces.get_prefix(Namespaces.ENTITY_BATCH)

    @staticmethod
    def process(changes: "StateChange"):
        LOG.info(f"Process changes with `EntityBatchHandler`: {changes.address}")
        entity_batch = EntityBatch()
        entity_batch.ParseFromString(changes.value)
        LOG.debug(f"Entity Batch: {entity_batch.id}")
        old_batch = r.table(Tbl.ENTITY_BATCHES).get(entity_batch.id).run()
        history = old_batch["history"] if old_batch else []
        timestamp = int(time.time())
        date = datetime.now().strftime("%Y-%m-%d")
        history.append(
            {
                "agent": entity_batch.owner_public_key,
                "timestamp": timestamp,
                "status": EntityBatch.Status.Name(entity_batch.status),
            }
        )

        for entity in entity_batch.entities:
            r.table(Tbl.ENTITY_EVENTS).insert(
                {
                    "batch_id": entity_batch.id,
                    "entity_id": entity.id,
                    "agent": entity_batch.owner_public_key,
                    "timestamp": timestamp,
                    "date": date,
                    "status": EntityBatch.Status.Name(entity_batch.status),
                }
            ).run()

        entities = [
            {
                "id": entity.id,
                "commodity_type": Entity.CommodityType.Name(entity.commodity_type),
                "generator_public_key": entity.generator_public_key,
            }
            for entity in entity_batch.entities
        ]

        r.table(Tbl.ENTITY_BATCHES).insert(
            {
                "id": entity_batch.id,
                "owner_public_key": entity_batch.owner_public_key,
                "status": EntityBatch.Status.Name(entity_batch.status),
                "finished": bool(entity_batch.finished),
                "history": history,
                "entities": entities,
            },
            conflict="update",
        ).run()
