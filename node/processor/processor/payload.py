from protos.agent_pb2 import Agent
from protos.payload_pb2 import SCPayload


class Payload:
    def __init__(self, payload):
        self._payload = SCPayload()
        self._payload.ParseFromString(payload)

    @staticmethod
    def from_bytes(payload):
        return Payload(payload=payload)

    @property
    def action(self):
        return self._payload.action

    @property
    def timestamp(self):
        return self._payload.timestamp

    @property
    def data(self):
        if self.action == SCPayload.CREATE_AGENT:
            return self._payload.create_agent
        if self.action == SCPayload.CREATE_ENTITY:
            return self._payload.create_entity
        if self.action == SCPayload.CREATE_ENTITY_BATCH:
            return self._payload.create_entity_batch
        if self.action == SCPayload.MOVE_ENTITY_BATCH:
            return self._payload.move_entity_batch
        if self.action == SCPayload.MOVE_ENTITY:
            return self._payload.move_entity
