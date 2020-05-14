from unittest.mock import MagicMock

from processor.handler import GaiachainTransactionHandler
from processor.payload import Payload
from protos.entity_pb2 import EntityBatch, Entity


class TestApply:
    def test_create_agent(self, create_agent_payload, agent):
        payload = Payload(create_agent_payload.SerializeToString())
        state = MagicMock()
        signer = agent.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)
        assert state.set_agent.called

    def test_create_entity(self, create_entity_payload, agent_producer):
        payload = Payload(create_entity_payload.SerializeToString())
        state = MagicMock()
        state.get_agent.return_value = agent_producer
        signer = agent_producer.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)
        assert state.set_entity.called

    def test_create_entity_batch(self, create_entity_batch_payload, agent):
        payload = Payload(create_entity_batch_payload.SerializeToString())
        state = MagicMock()
        signer = agent.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)
        assert state.set_entity.called
        assert state.set_entity_batch.called

    def test_move_entity_batch_from_producer_arrived_to_departed(
        self,
        move_entity_batch_payload_producer_arrived,
        entity_batch_producer_arrived,
        agent_producer,
    ):
        payload = Payload(
            move_entity_batch_payload_producer_arrived.SerializeToString()
        )
        state = MagicMock()
        state.get_entity_batch.return_value = entity_batch_producer_arrived
        state.get_agent.side_effect = [agent_producer, agent_producer]
        signer = agent_producer.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)
        expected_batch = EntityBatch()
        expected_batch.CopyFrom(entity_batch_producer_arrived)
        expected_batch.status = EntityBatch.DEPARTED
        state.set_entity_batch.assert_called_with(expected_batch)

    def test_move_entity_batch_from_producer_departed_to_logpark_arrived(
        self,
        move_entity_batch_payload_producer_departed,
        entity_batch_producer_departed,
        agent_logpark,
        agent_producer,
    ):
        payload = Payload(
            move_entity_batch_payload_producer_departed.SerializeToString()
        )
        state = MagicMock()
        state.get_entity_batch.return_value = entity_batch_producer_departed
        state.get_agent.side_effect = [agent_producer, agent_logpark]
        signer = agent_logpark.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)
        expected_batch = EntityBatch()
        expected_batch.CopyFrom(entity_batch_producer_departed)
        expected_batch.owner_public_key = signer
        expected_batch.status = EntityBatch.ARRIVED
        state.set_entity_batch.assert_called_with(expected_batch)

    def test_move_entity_batch_from_exporter_arrived_to_departed_and_finish(
        self,
        move_entity_batch_payload_exporter_arrived,
        entity_batch_exporter_arrived,
        agent_exporter,
    ):
        payload = Payload(
            move_entity_batch_payload_exporter_arrived.SerializeToString()
        )
        state = MagicMock()
        state.get_entity_batch.return_value = entity_batch_exporter_arrived
        state.get_agent.side_effect = [agent_exporter, agent_exporter]
        signer = agent_exporter.public_key
        handler = GaiachainTransactionHandler()
        handler._apply_action(payload, state, signer)

        called_args_eb = state.set_entity_batch.call_args[0][0]
        assert called_args_eb.owner_public_key == signer
        assert called_args_eb.status == EntityBatch.DEPARTED
        assert called_args_eb.finished is True
        assert called_args_eb.id == entity_batch_exporter_arrived.id

        called_args_e = state.set_entity.call_args[0][0]
        assert called_args_e.finished_timestamp > 0
