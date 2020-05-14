import hashlib
from unittest.mock import MagicMock

import pytest

from processor.state import State
from protos.agent_pb2 import Agent
from protos.entity_pb2 import Entity, EntityBatch
from protos.payload_pb2 import (
    SCPayload,
    CreateAgentAction,
    CreateEntityAction,
    CreateEntityBatchAction,
    MoveEntityBatchAction,
)


@pytest.fixture
def state():
    context = MagicMock()
    state = State(context)
    return state


@pytest.fixture()
def agent_factory(faker):
    class Factory:
        def get(self):
            agent = Agent(
                company_name=f"{faker.company()} {faker.company_suffix()}",
                email=faker.email(),
                timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
                role=faker.random_element(
                    elements=(
                        Agent.PRODUCER,
                        Agent.LOG_PARK,
                        Agent.SAWMILL,
                        Agent.EXPORTER,
                    )
                ),
                public_key=hashlib.sha512(
                    (faker.pystr(min_chars=1, max_chars=5)).encode("utf-8")
                ).hexdigest()[:66],
            )
            agent.location.lat = int(faker.latitude() * 1_000_000)
            agent.location.long = int(faker.longitude() * 1_000_000)
            return agent

    return Factory()


@pytest.fixture()
def agent(agent_factory):
    return agent_factory.get()


@pytest.fixture()
def agent_producer(agent):
    agent_ = Agent()
    agent_.CopyFrom(agent)
    agent_.role = Agent.PRODUCER
    return agent_


@pytest.fixture()
def agent_logpark(agent):
    agent_ = Agent()
    agent_.CopyFrom(agent)
    agent_.role = Agent.LOG_PARK
    return agent_


@pytest.fixture()
def agent_sawmill(agent):
    agent.role = Agent.SAWMILL
    return agent


@pytest.fixture()
def agent_exporter(agent):
    agent_ = Agent()
    agent_.CopyFrom(agent)
    agent_.role = Agent.EXPORTER
    return agent_


@pytest.fixture()
def uninitialized_entity(faker, agent_producer):
    entity = Entity(
        id=f"{faker.pystr(min_chars=4, max_chars=4)}"
        f"-{faker.pystr(min_chars=4, max_chars=4)}"
        f"-{faker.pystr(min_chars=4, max_chars=4)}",
        generator_public_key=agent_producer.public_key,
        generation_timestamp=faker.random_int(min=1_500_000_000, max=1_535_000_000),
        commodity_type=Entity.TIMBER,
    )
    return entity


@pytest.fixture()
def initialized_entity(faker, agent_producer, agent_factory):
    agent = agent_factory.get()
    agent.role = faker.random_element(
        elements=(Agent.LOG_PARK, Agent.SAWMILL, Agent.EXPORTER)
    )
    entity = Entity(
        id=f"{faker.pystr(min_chars=4, max_chars=4)}"
        f"-{faker.pystr(min_chars=4, max_chars=4)}"
        f"-{faker.pystr(min_chars=4, max_chars=4)}",
        generator_public_key=agent_producer.public_key,
        generation_timestamp=faker.random_int(min=1_500_000_000, max=1_535_000_000),
        commodity_type=Entity.TIMBER,
        assignment_timestamp=faker.random_int(min=1_535_000_000, max=1_545_000_000),
        # todo: entity_batch
    )
    return entity


@pytest.fixture()
def entity(faker, initialized_entity, uninitialized_entity):
    return faker.random_element(elements=(initialized_entity, uninitialized_entity))


@pytest.fixture()
def entity_batch(faker, initialized_entity, agent_factory):
    owner = agent_factory.get()
    entity_batch = EntityBatch(
        id=initialized_entity.id,
        owner_public_key=owner.public_key,
        entities=[initialized_entity],
        status=faker.random_element(
            elements=(EntityBatch.ARRIVED, EntityBatch.DEPARTED)
        ),
    )
    return entity_batch


@pytest.fixture()
def entity_batch_producer_arrived(agent_producer, initialized_entity):
    entity_batch = EntityBatch(
        id=initialized_entity.id,
        owner_public_key=agent_producer.public_key,
        entities=[initialized_entity],
        status=EntityBatch.ARRIVED,
    )
    return entity_batch


@pytest.fixture()
def entity_batch_producer_departed(agent_producer, initialized_entity):
    entity_batch = EntityBatch(
        id=initialized_entity.id,
        owner_public_key=agent_producer.public_key,
        entities=[initialized_entity],
        status=EntityBatch.DEPARTED,
    )
    return entity_batch


@pytest.fixture()
def entity_batch_exporter_arrived(agent_exporter, initialized_entity):
    entity_batch = EntityBatch(
        id=initialized_entity.id,
        owner_public_key=agent_exporter.public_key,
        entities=[initialized_entity],
        status=EntityBatch.ARRIVED,
    )
    return entity_batch


@pytest.fixture
def create_agent_payload(faker, agent):
    payload = SCPayload(
        action=SCPayload.CREATE_AGENT,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        create_agent=CreateAgentAction(agent=agent),
    )
    return payload


@pytest.fixture
def create_entity_payload(faker, uninitialized_entity):
    payload = SCPayload(
        action=SCPayload.CREATE_ENTITY,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        create_entity=CreateEntityAction(entity=uninitialized_entity),
    )
    return payload


@pytest.fixture
def create_entity_batch_payload(faker, uninitialized_entity):
    payload = SCPayload(
        action=SCPayload.CREATE_ENTITY_BATCH,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        create_entity_batch=CreateEntityBatchAction(entities=[uninitialized_entity]),
    )
    return payload


@pytest.fixture
def move_entity_batch_payload(faker, entity_batch):
    payload = SCPayload(
        action=SCPayload.MOVE_ENTITY_BATCH,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        move_entity_batch=MoveEntityBatchAction(
            entity_batch_id=entity_batch.id,
            status=faker.random_element(
                elements=(EntityBatch.ARRIVED, EntityBatch.DEPARTED)
            ),
        ),
    )
    return payload


@pytest.fixture
def move_entity_batch_payload_producer_arrived(faker, entity_batch_producer_arrived):
    payload = SCPayload(
        action=SCPayload.MOVE_ENTITY_BATCH,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        move_entity_batch=MoveEntityBatchAction(
            entity_batch_id=entity_batch_producer_arrived.id,
            status=EntityBatch.DEPARTED,
        ),
    )
    return payload


@pytest.fixture
def move_entity_batch_payload_producer_departed(faker, entity_batch_producer_departed):
    payload = SCPayload(
        action=SCPayload.MOVE_ENTITY_BATCH,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        move_entity_batch=MoveEntityBatchAction(
            entity_batch_id=entity_batch_producer_departed.id,
            status=EntityBatch.ARRIVED,
        ),
    )
    return payload


@pytest.fixture
def move_entity_batch_payload_exporter_arrived(faker, entity_batch_exporter_arrived):
    payload = SCPayload(
        action=SCPayload.MOVE_ENTITY_BATCH,
        timestamp=faker.random_int(min=1_500_000_000, max=1_545_000_000),
        move_entity_batch=MoveEntityBatchAction(
            entity_batch_id=entity_batch_exporter_arrived.id,
            status=EntityBatch.DEPARTED,
        ),
    )
    return payload
