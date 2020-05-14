from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChange


class HandlerBase:
    prefix: str = None

    @staticmethod
    def process(changes: "StateChange"):
        raise NotImplemented()
