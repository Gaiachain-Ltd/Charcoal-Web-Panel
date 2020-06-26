import logging
from concurrent.futures import TimeoutError as ConcurrentTimeoutError, CancelledError

from sawtooth_sdk.messaging.exceptions import ValidatorConnectionError
from sawtooth_sdk.messaging.future import FutureTimeoutError
from sawtooth_sdk.messaging.stream import Stream, RECONNECT_EVENT
from sawtooth_sdk.protobuf.client_event_pb2 import ClientEventsSubscribeRequest
from sawtooth_sdk.protobuf.events_pb2 import EventList, EventSubscription, EventFilter
from sawtooth_sdk.protobuf.network_pb2 import PingResponse
from sawtooth_sdk.protobuf.processor_pb2 import TpRegisterResponse
from sawtooth_sdk.protobuf.transaction_receipt_pb2 import StateChangeList
from sawtooth_sdk.protobuf.validator_pb2 import Message
from typing import TYPE_CHECKING, Optional, Type

from protos.enums import Namespaces

if TYPE_CHECKING:
    from concurrent.futures import Future
    from apps.blockchain.handlers._base import HandlerBase

LOG = logging.getLogger(__name__)

VALIDATOR_URL = "tcp://validator:4004"
NULL_BLOCK_ID = "0000000000000000"


class SyncProcessor:
    future: Optional["Future"] = None
    _stream: Stream

    def __init__(self, url=None):
        self._stream = Stream(url or VALIDATOR_URL)
        self._handlers = []

    def add_handler(self, handler: Type["HandlerBase"]):
        if handler not in self._handlers:
            LOG.info(f"Add handler {handler.__name__}")
            self._handlers.append(handler)

    def start(self):
        LOG.info("Start SyncProcessor")

        future = None
        try:
            self._register()
            while True:
                future = self._stream.receive()
                self._process_future(future)
        except KeyboardInterrupt:
            LOG.warning("break")
            try:
                # tell the validator to not send any more messages
                self._unregister()
                while True:
                    if future is not None:
                        # process futures as long as the tp has them,
                        # if the TP_PROCESS_REQUEST doesn't come from
                        # zeromq->asyncio in 1 second raise a
                        # concurrent.futures.TimeOutError and be done.
                        self._process_future(future, 1, sigint=True)
                        future = self._stream.receive()
            except ConcurrentTimeoutError:
                # Where the tp will usually exit after
                # a KeyboardInterrupt. Caused by the 1 second
                # timeout in _process_future.
                pass
            except FutureTimeoutError:
                # If the validator is not able to respond to the
                # unregister request, exit.
                pass

    def _unregister(self):
        LOG.warning("unregister")
        pass

    def _register(self):
        LOG.debug(f"Register handlers")
        self._stream.wait_for_ready()
        future = self._stream.send(
            message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
            content=ClientEventsSubscribeRequest(
                last_known_block_ids=[NULL_BLOCK_ID],
                subscriptions=[
                    EventSubscription(event_type="sawtooth/block-commit"),
                    EventSubscription(
                        event_type="sawtooth/state-delta",
                        filters=[
                            EventFilter(
                                key="address",
                                match_string=f"^{Namespaces.GA_NAMESPACE}.*",
                                filter_type=EventFilter.REGEX_ANY,
                            )
                        ],
                    ),
                ],
            ).SerializeToString(),
        )

        resp = TpRegisterResponse()
        try:
            resp.ParseFromString(future.result().content)
            LOG.info(
                "Register response: %s", TpRegisterResponse.Status.Name(resp.status)
            )
        except ValidatorConnectionError as vce:
            LOG.info("During waiting for response on registration: %s", vce)
        except Exception as e:
            LOG.info("During waiting for response on registration: %s", e)

    def _process_future(self, future: "Future", timeout=None, sigint=False) -> None:
        try:
            msg = future.result(timeout)
        except CancelledError:
            # This error is raised when Task.cancel is called on
            # disconnect from the validator in stream.py, for
            # this future.
            LOG.error("Cancelled")
            return

        if msg is RECONNECT_EVENT:
            if sigint is False:
                LOG.info("Reregistering with validator")
                self._stream.wait_for_ready()
                self._register()
        else:
            LOG.debug(
                f"Received message of type: "
                f"{Message.MessageType.Name(msg.message_type)}"
            )

            if msg.message_type == Message.PING_REQUEST:
                self._stream.send_back(
                    message_type=Message.PING_RESPONSE,
                    correlation_id=msg.correlation_id,
                    content=PingResponse().SerializeToString(),
                )
                return
            elif msg.message_type == Message.CLIENT_EVENTS:
                self._process(msg)
                return

            LOG.warning(
                f"SyncProcessor got wrong message type: "
                f"{Message.MessageType.Name(msg.message_type)}"
            )

    def _process(self, msg: Message) -> None:
        event_list = EventList()
        event_list.ParseFromString(msg.content)
        events = event_list.events
        raw_block = next(
            (e for e in events if e.event_type == "sawtooth/block-commit"), []
        )
        block = {b.key: b.value for b in raw_block.attributes}
        LOG.debug(f"Block: {block}")
        event = next(
            (e for e in events if e.event_type == "sawtooth/state-delta"), None
        )
        if event:
            state_changes = StateChangeList()
            state_changes.ParseFromString(event.data)
            changes = list(state_changes.state_changes)
            LOG.debug(f"Found {len(changes)} state changes")
            self._handle_changes(block, changes)

    def _handle_changes(self, block: dict, changes: list):
        # r.table(Tbl.BLOCKS).insert(block).run()
        for change in changes:
            for handler in self._handlers:
                if change.address.startswith(handler.prefix):
                    handler.process(change)
