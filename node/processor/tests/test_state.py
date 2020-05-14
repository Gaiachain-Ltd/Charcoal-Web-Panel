from sawtooth_sdk.protobuf.state_context_pb2 import TpStateEntry

from protos.agent_pb2 import AgentContainer
from protos.enums import Namespaces


class TestAgent:
    def test_set_agent(self, state, agent):
        mock = state._context.set_state

        state.set_agent(agent)
        address = Namespaces.get_address(
            agent.public_key, subnamespace=Namespaces.AGENT
        )
        ac = AgentContainer(entries=[agent])
        mock.assert_called_with({address: ac.SerializeToString()})

    def test_get_agent(self, state, agent):
        mock = state._context.get_state
        address = Namespaces.get_address(
            agent.public_key, subnamespace=Namespaces.AGENT
        )
        ac = AgentContainer(entries=[agent]).SerializeToString()
        entry = TpStateEntry(address=address, data=ac)
        mock.return_value = [entry]
        returned_agent = state.get_agent(agent.public_key)

        mock.assert_called_with([address])
        assert returned_agent == agent


class TestEntity:
    def test_set_entity(self, state, entity):
        mock = state._context.set_state

        state.set_entity(entity)
        address = Namespaces.get_address(entity.id, subnamespace=Namespaces.ENTITY)
        mock.assert_called_with({address: entity.SerializeToString()})

    def test_get_entity(self, state, entity):
        mock = state._context.get_state
        address = Namespaces.get_address(entity.id, subnamespace=Namespaces.ENTITY)
        entry = TpStateEntry(address=address, data=entity.SerializeToString())
        mock.return_value = [entry]
        returned_entity = state.get_entity(entity.id)

        mock.assert_called_with([address])
        assert returned_entity == entity


class TestBatch:
    def test_set_batch(self, state, entity_batch):
        mock = state._context.set_state

        state.set_entity_batch(entity_batch)
        address = Namespaces.get_address(
            entity_batch.id, subnamespace=Namespaces.ENTITY_BATCH
        )
        mock.assert_called_with({address: entity_batch.SerializeToString()})

    def test_get_batch(self, state, entity_batch):
        mock = state._context.get_state

        address = Namespaces.get_address(
            entity_batch.id, subnamespace=Namespaces.ENTITY_BATCH
        )
        entry = TpStateEntry(address=address, data=entity_batch.SerializeToString())
        mock.return_value = [entry]
        returned_entity_batch = state.get_entity_batch(entity_batch.id)

        mock.assert_called_with([address])
        assert returned_entity_batch == entity_batch
