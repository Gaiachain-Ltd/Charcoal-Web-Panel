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
        if self.action == SCPayload.CREATE_PACKAGE:
            return self._payload.create_package
        if self.action == SCPayload.UPDATE_PACKAGE:
            return self._payload.update_package
        if self.action == SCPayload.CREATE_REPLANTATION:
            return self._payload.create_replantation
