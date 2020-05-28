import logging

from sawtooth_sdk.processor.handler import TransactionHandler

from processor.payload import Payload
from processor.state import State
from protos.agent_pb2 import Agent
from protos.entity_pb2 import EntityBatch, Entity, Package
from protos.enums import Gaiachain, Namespaces
from protos.payload_pb2 import SCPayload

LOG = logging.getLogger(__name__)


class GaiachainTransactionHandler(TransactionHandler):
    @property
    def family_name(self):
        return Gaiachain.FAMILY_NAME

    @property
    def family_versions(self):
        return [Gaiachain.FAMILY_VERSION]

    @property
    def namespaces(self):
        return [Namespaces.GA_NAMESPACE]

    def apply(self, transaction, context):
        header = transaction.header
        signer = header.signer_public_key
        payload = Payload.from_bytes(transaction.payload)
        state = State(context)
        self._apply_action(payload, state, signer)

    def _apply_action(self, payload: Payload, state: State, signer: str):
        if payload.action == SCPayload.CREATE_AGENT:
            self._create_agent(payload, state, signer)
        elif payload.action == SCPayload.CREATE_PACKAGE:
            self._create_package(payload, state, signer)
        elif payload.action == SCPayload.UPDATE_PACKAGE:
            self._update_package(payload, state, signer)
        elif payload.action == SCPayload.CREATE_ENTITY_BATCH:
            self._create_entity_batch(payload, state, signer)
        elif payload.action == SCPayload.MOVE_ENTITY_BATCH:
            self._move_entity_batch(payload, state, signer)

    def _create_agent(self, payload: Payload, state: State, signer: str):
        agent = payload.data.agent
        agent.public_key = signer
        agent.timestamp = payload.timestamp
        LOG.info(f"Create agent: {payload.data.agent.email}")
        state.set_agent(agent)

    def _create_package(self, payload: Payload, state: State, signer: str):
        agent = state.get_agent(signer)
        package = payload.data.package
        package_type = package.type
        if not self._allowed_to_create_package(agent, package_type):
            LOG.warning(f"This user can't create a package of type {package.type}.")
            return

        if package_type == Package.HARVEST:
            plot = state.get_package(package.plot.id)
            package.plot.CopyFrom(plot)
        elif package_type == Package.TRUCK:
            harvest = state.get_package(package.harvest.id)
            package.harvest.CopyFrom(harvest)
        LOG.info(f"Create package: {package.id}")
        LOG.info(package)
        state.set_package(package)

    def _update_package(self, payload: Payload, state: State, signer: str):
        package_id = payload.data.id
        package = state.get_package(package_id)

        agent = state.get_agent(signer)
        try:
            entity = payload.data.entity

            if self._allowed_to_add_entity_to_package(agent, entity.status):
                entities = [e for e in package.entities]
                entities.append(entity)
                del package.entities[:]
                package.entities.extend(entities)
                state.set_package(package)
                LOG.info(f"Update package {package.id}")
                LOG.info(package)
                return
        except AttributeError as e:
            LOG.info(f"Error {e}")

    def _create_entity_batch(self, payload: Payload, state: State, signer: str):
        entities = payload.data.entities
        # todo: use proper generator in full app
        batch_id = entities[0].id

        for entity in entities:
            entity.entity_batch_id = batch_id
            # entity.assignment_timestamp = payload.timestamp
            state.set_entity(entity)

        entity_batch = EntityBatch(
            id=batch_id,
            # owner_public_key=signer,
            entities=entities,
            status=Entity.HARVEST,
        )
        state.set_entity_batch(entity_batch)

    def _move_entity_batch(self, payload: Payload, state: State, signer: str):
        entity_batch_id = payload.data.entity_batch_id
        entity_batch = state.get_entity_batch(entity_batch_id)

        # owner = state.get_agent(entity_batch.owner_public_key)
        agent = state.get_agent(signer)
        status = entity_batch.status
        new_status = payload.data.status

        if self._allowed_to_change_status(agent, status, new_status):
            # entity_batch.owner_public_key = signer
            entity_batch.status = new_status
            # if self._should_finish(agent, new_status):
            #     entity_batch.finished = True
            #     for entity in entity_batch.entities:
            #         entity.finished_timestamp = payload.timestamp
            #         state.set_entity(entity)
            keys = []
            if new_status == Entity.GRAIN_PROCESSING:
                keys = ['breaking_date', 'end_fermentation_date', 'beans_volume']
            elif new_status == Entity.SECTION_RECEPTION:
                keys = ['reception_date', 'transport_date', 'buyer']
            for entity in entity_batch.entities:
                for key in keys:
                    setattr(entity, key, getattr(payload.data, key))
                state.set_entity(entity)

            state.set_entity_batch(entity_batch)
            return

        # if self._allowed_to_move_between_agents(owner, agent, status, new_status):
        #     entity_batch.owner_public_key = signer
        #     entity_batch.status = new_status
        #     state.set_entity_batch(entity_batch)

    def _allowed_to_add_entity_to_package(
        self,
        signer: Agent,
        status: Entity.Status,
    ):
        if signer is None:
            return False
        return signer.role == Agent.SUPER_USER or (
            signer.role == Agent.CARBONIZER
            and status in (Entity.LOGGING_ENDING, Entity.CARBONIZATION_BEGINNING, Entity.CARBONIZATION_ENDING)
        ) or (
            signer.role == Agent.LOGGER
            and status == Entity.LOGGING_ENDING
        ) or (
            signer.role == Agent.DIRECTOR
            and status == Entity.RECEPTION
        )

    def _allowed_to_create_package(
        self,
        signer: Agent,
        type: Package.PackageType,
    ):
        if signer is None:
            return False
        # CARBONIZER is allowed to create PLOT, HARVEST and TRUCK packages
        return signer.role in (Agent.SUPER_USER, Agent.CARBONIZER) or (
            signer.role == Agent.LOGGER
            and type == Package.PLOT
        )
