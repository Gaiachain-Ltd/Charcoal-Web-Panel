from processor.payload import Payload
from protos.payload_pb2 import SCPayload


class TestPayload:
    def test_create_agent_payload(self, create_agent_payload):
        payload = create_agent_payload.SerializeToString()
        p = Payload(payload)
        assert p.action == SCPayload.CREATE_AGENT
        assert p.timestamp == create_agent_payload.timestamp
        assert p.data == create_agent_payload.create_agent

    def test_create_entity_payload(self, create_entity_payload):
        payload = create_entity_payload.SerializeToString()
        p = Payload(payload)
        assert p.action == SCPayload.CREATE_ENTITY
        assert p.timestamp == create_entity_payload.timestamp
        assert p.data == create_entity_payload.create_entity

    def test_create_entity_batch_payload(self, create_entity_batch_payload):
        payload = create_entity_batch_payload.SerializeToString()
        p = Payload(payload)
        assert p.action == SCPayload.CREATE_ENTITY_BATCH
        assert p.timestamp == create_entity_batch_payload.timestamp
        assert p.data == create_entity_batch_payload.create_entity_batch

    def test_move_entity_batch_payload(self, move_entity_batch_payload):
        payload = move_entity_batch_payload.SerializeToString()
        p = Payload(payload)
        assert p.action == SCPayload.MOVE_ENTITY_BATCH
        assert p.timestamp == move_entity_batch_payload.timestamp
        assert p.data == move_entity_batch_payload.move_entity_batch
