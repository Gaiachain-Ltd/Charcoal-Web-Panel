import logging

from protos.agent_pb2 import Agent, AgentContainer
from protos.entity_pb2 import Entity, Package, Replantation
from protos.enums import Namespaces

LOG = logging.getLogger(__name__)


class State:
    TIMEOUT = 3

    def __init__(self, context):
        self._context = context

    def set_agent(self, agent: Agent):
        LOG.info(f"Set agent `{agent.public_key}`")
        address = Namespaces.get_address(
            agent.public_key, subnamespace=Namespaces.AGENT
        )
        agents = AgentContainer(entries=[agent])
        self._context.set_state({address: agents.SerializeToString()})

    def get_agent(self, public_key: str):
        LOG.info(f"Get agent `{public_key}`")
        address = Namespaces.get_address(public_key, subnamespace=Namespaces.AGENT)
        agents = self._context.get_state([address])
        if not agents:
            LOG.warning("No agents found.")
            return
        container = AgentContainer()
        container.ParseFromString(agents[0].data)
        if len(container.entries) > 1:
            LOG.warning("Found more than one agent. Return first")
        elif len(container.entries) == 0:
            LOG.warning("No agents found in container.")
            return

        return container.entries.pop(0)

    def set_package(self, package: Package):
        address = Namespaces.get_address(package.id, subnamespace=Namespaces.PACKAGE)
        self._context.set_state({address: package.SerializeToString()})

    def get_package(self, package_id: str):
        address = Namespaces.get_address(package_id, subnamespace=Namespaces.PACKAGE)
        package_list = self._context.get_state([address])

        if not package_list:
            LOG.warning("No packages found.")
            return

        package = Package()
        package.ParseFromString(package_list[0].data)
        return package

    def set_replantation(self, replantation: Replantation):
        address = Namespaces.get_address(str(replantation.id), subnamespace=Namespaces.REPLANTATION)
        self._context.set_state({address: replantation.SerializeToString()})