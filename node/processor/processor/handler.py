import logging

from sawtooth_sdk.processor.handler import TransactionHandler

from processor.payload import Payload
from processor.state import State
from protos.agent_pb2 import Agent
from protos.entity_pb2 import EntityBatch, Entity
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
        elif payload.action == SCPayload.CREATE_ENTITY:
            self._create_entity(payload, state, signer)
        elif payload.action == SCPayload.CREATE_ENTITY_BATCH:
            self._create_entity_batch(payload, state, signer)
        elif payload.action == SCPayload.MOVE_ENTITY_BATCH:
            self._move_entity_batch(payload, state, signer)
        elif payload.action == SCPayload.MOVE_ENTITY:
            self._move_entity(payload, state, signer)

    def _create_agent(self, payload: Payload, state: State, signer: str):
        agent = payload.data.agent
        agent.public_key = signer
        agent.timestamp = payload.timestamp
        LOG.info(f"Create agent: {payload.data.agent.email}")
        state.set_agent(agent)

    def _create_entity(self, payload: Payload, state: State, signer: str):
        agent = state.get_agent(signer)

        entity = payload.data.entity
        status = entity.status
        if not self._allowed_to_create_entity(agent, status):
            LOG.warning(f"This user can't create an entity of type {entity.package_type}.")
            return

        if status in [Entity.BAGGING, Entity.LOT_CREATION]:
            entities = []
            for sub_entity_data in entity.entities:
                sub_entity = state.get_entity(sub_entity_data.id)
                if sub_entity:
                    if status == Entity.BAGGING:
                        sub_entity.sac_id = entity.id
                        sub_entity.weight = sub_entity_data.weight
                    elif status == Entity.LOT_CREATION:
                        sub_entity.lot_id = entity.id
                    state.set_entity(sub_entity)
                    entities.append(sub_entity)
                else:
                    LOG.warning(f"Entity {entity.id} SubEntity not found: {sub_entity_data.id}")
            del entity.entities[:]
            entity.entities.extend(entities)
        entity.timestamp = payload.timestamp
        LOG.info(f"Create entity: {entity.id}")
        LOG.info(entity)
        state.set_entity(entity)

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

    def _move_entity(self, payload: Payload, state: State, signer: str):
        entity_id = payload.data.id
        entity = state.get_entity(entity_id)

        agent = state.get_agent(signer)
        try:
            status = entity.status
            new_status = payload.data.status

            if self._allowed_to_change_status(agent, status, new_status):
                entity.status = new_status
                entity.timestamp = payload.timestamp
                keys = []
                if new_status == Entity.GRAIN_PROCESSING:
                    keys = ['breaking_date', 'end_fermentation_date', 'beans_volume']
                elif new_status == Entity.SECTION_RECEPTION:
                    keys = ['reception_date', 'transport_date', 'buyer']
                elif new_status == Entity.WAREHOUSE_TRANSPORT:
                    keys = ['transporter', 'transport_date', 'destination']
                elif new_status == Entity.EXPORT_RECEPTION:
                    keys = ['weight']
                for key in keys:
                    setattr(entity, key, getattr(payload.data, key))
                entity.user.CopyFrom(agent)
                state.set_entity(entity)
                LOG.info(f"Update entity {entity.id}")
                LOG.info(entity)
                return
        except AttributeError as e:
            LOG.info(f"Error {e}")

    def _allowed_to_change_status(
        self,
        signer: Agent,
        status: Entity.Status,
        new_status: Entity.Status,
    ):
        if signer is None:
            return False
        return signer.role == Agent.SUPER_USER or (
            signer.role == Agent.INSPECTOR
            and status == Entity.HARVESTING
            and new_status == Entity.GRAIN_PROCESSING
        ) or (
            signer.role in (Agent.PCA, Agent.WAREHOUSEMAN)
            and status == Entity.GRAIN_PROCESSING
            and new_status == Entity.SECTION_RECEPTION
        ) or (
            signer.role == Agent.WAREHOUSEMAN
            and status == Entity.LOT_CREATION
            and new_status == Entity.WAREHOUSE_TRANSPORT
        ) or (
            signer.role == Agent.COOPERATIVE
            and status == Entity.WAREHOUSE_TRANSPORT
            and new_status == Entity.EXPORT_RECEPTION
        )

    def _allowed_to_create_entity(
        self,
        signer: Agent,
        status: Entity.Status,
    ):
        if signer is None:
            return False
        return signer.role == Agent.SUPER_USER or (
            signer.role == Agent.INSPECTOR
            and status == Entity.HARVESTING
        ) or (
            signer.role in (Agent.PCA, Agent.WAREHOUSEMAN)
            and status in [Entity.BAGGING, Entity.LOT_CREATION]
        )
