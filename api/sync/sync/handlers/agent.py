import logging

import rethinkdb as r
from typing import TYPE_CHECKING

from protos.agent_pb2 import AgentContainer
from protos.enums import Namespaces, Tbl
from sync.handlers._base import HandlerBase

LOG = logging.getLogger(__name__)

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class AgentHandler(HandlerBase):
    prefix = Namespaces.get_prefix(Namespaces.AGENT)

    @staticmethod
    def process(changes: "StateChange"):
        LOG.info(f"Process changes with `AgentHandler`: {changes.address}")
        container = AgentContainer()
        container.ParseFromString(changes.value)
        agent = container.entries[0]
        LOG.debug(f"Agent: {agent.email} ({agent.company_name})")
        r.table(Tbl.AGENTS).insert(
            {
                "email": agent.email,
                "ref": changes.address,
                "public_key": agent.public_key,
                "timestamp": agent.timestamp,
            },
            conflict="update",
        ).run()
