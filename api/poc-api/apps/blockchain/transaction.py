# -*- coding: utf-8 -*-
import hashlib
import time

from enum import Enum
from typing import List, Any, TYPE_CHECKING


from sawtooth_sdk.protobuf.batch_pb2 import Batch, BatchList, BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_signing import CryptoFactory

from protos.agent_pb2 import Agent
from protos.entity_pb2 import Entity, EntityBatch, Package
from protos.enums import Gaiachain, Namespaces
from protos.payload_pb2 import SCPayload

from .api_requests import APIRequests
from .sawtooth import swt


if TYPE_CHECKING:
    from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
    from sawtooth_signing import Signer


class PayloadFactory:
    """Factory for creating SCPayload."""

    class Types(Enum):
        """Action types"""

        CREATE_AGENT = "_create_agent_action"
        CREATE_ENTITY = "_create_entity_action"
        CREATE_PACKAGE = "_create_package_action"
        CREATE_ENTITY_BATCH = "_create_entity_batch_action"
        UPDATE_ENTITY_BATCH = "_update_entity_batch_action"
        UPDATE_PACKAGE = "_update_package_action"

    @staticmethod
    def _create_agent_action(proto: Agent, **kwargs) -> SCPayload:
        payload = PayloadFactory._create_payload()
        payload.action = SCPayload.CREATE_AGENT
        payload.create_agent.agent.CopyFrom(proto)
        return payload

    @staticmethod
    def _create_package_action(proto: Package, **kwargs) -> SCPayload:
        payload = PayloadFactory._create_payload()
        payload.action = SCPayload.CREATE_PACKAGE
        payload.create_package.package.CopyFrom(proto)
        return payload

    @staticmethod
    def _create_entity_batch_action(proto: List[Entity], **kwargs) -> SCPayload:
        payload = PayloadFactory._create_payload()
        payload.action = SCPayload.CREATE_ENTITY_BATCH
        payload.create_entity_batch.entities.extend(proto)
        return payload

    @staticmethod
    def _update_entity_batch_action(proto: dict, **kwargs) -> SCPayload:
        payload = PayloadFactory._create_payload()
        payload.action = SCPayload.MOVE_ENTITY_BATCH
        payload.move_entity_batch.entity_batch_id = proto.get("entity_batch_id")
        status = proto.get("status")
        payload.move_entity_batch.status = status

        keys = []
        if status == EntityBatch.Status.Value('GRAIN_PROCESSING'):
            keys = ['breaking_date', 'end_fermentation_date', 'beans_volume']
        elif status == EntityBatch.Status.Value('SECTION_RECEPTION'):
            keys = ['reception_date', 'transport_date', 'buyer']
        for key in keys:
            setattr(payload.move_entity_batch, key, proto.get(key))
        return payload

    @staticmethod
    def _update_package_action(proto: dict, **kwargs) -> SCPayload:
        payload = PayloadFactory._create_payload()
        payload.action = SCPayload.UPDATE_PACKAGE
        payload.update_package.id = proto.get("id")
        payload.update_package.entity.CopyFrom(proto.get('entity'))
        return payload

    @staticmethod
    def _create_payload() -> SCPayload:
        return SCPayload(timestamp=int(time.time()))

    @classmethod
    def create(cls, type_: Types, **kwargs) -> SCPayload:
        """Create payload based on type.

        Args:
            type_: Type of payload.
            **kwargs: Params required for type.

        Returns:
            SCPayload instance.
        """
        return getattr(PayloadFactory, type_.value)(**kwargs)

    @classmethod
    def create_encoded(cls, type_: Types, **kwargs) -> bytes:
        """Create payload based on type.

        Args:
            type_: Type of payload.
            **kwargs: Params required for type.

        Returns:
            Bytes for SCPayload instance.

        Example:
            payload = Payload.create(
                Payload.Types.CREATE_AGENT, name="Jon Snow")
            >> b'\x10\xd9\xf6\x9e\xe1\x05\x1a\n\n\x08Jon Snow'

            which is equivalent to:
            SCPayload(
                action=SCPayload.CREATE_AGENT,
                timestamp=<now>,
                create_agent = CreateAgentAction(
                    name="Jon Snow"
                )
            ).SerializeToString()
        """
        return cls.create(type_, **kwargs).SerializeToString()


class TransactionFactory:
    """Factory for creating signed Transaction."""

    @classmethod
    def _get_header(cls, signer: "Signer", payload: bytes) -> TransactionHeader:
        signer_hex = signer.get_public_key().as_hex()
        addresses = [Namespaces.GA_NAMESPACE]
        return TransactionHeader(
            family_name=Gaiachain.FAMILY_NAME,
            family_version=Gaiachain.FAMILY_VERSION,
            inputs=addresses,
            outputs=addresses,
            signer_public_key=signer_hex,
            batcher_public_key=signer_hex,
            dependencies=[],
            payload_sha512=hashlib.sha512(payload).hexdigest(),
        )

    @classmethod
    def _get_header_bytes(cls, signer: "Signer", payload: bytes) -> bytes:
        return cls._get_header(signer, payload).SerializeToString()

    @classmethod
    def _get_signature(cls, signer: "Signer", header: bytes) -> str:
        return signer.sign(header)

    @classmethod
    def _create_transaction(cls, signer, payload: bytes):
        header_bytes = TransactionFactory._get_header_bytes(signer, payload)
        signature = TransactionFactory._get_signature(signer, header_bytes)
        return Transaction(
            header=header_bytes, header_signature=signature, payload=payload
        )

    @classmethod
    def create(cls, signer: "Signer", payload: bytes) -> Transaction:
        """Create signed Transaction from given payload.

        Args:
            signer: Signer instance.
            payload: Bytes of Payload.

        Returns:
            Transaction instance.
        """
        return cls._create_transaction(signer, payload)

    @classmethod
    def create_encoded(cls, signer: "Signer", payload: bytes) -> bytes:
        """Create encoded, signed Transaction from given payload.

        Args:
            signer: Signer instance.
            payload: Bytes of Payload.
            address: State address.

        Returns:
            Bytes for Transaction instance.
        """
        return cls.create(signer, payload).SerializeToString()


class BatchFactory:
    """Factory for creating signed Batch from list of transactions."""

    @classmethod
    def _get_header(
        cls, signer: "Signer", transactions: List[Transaction]
    ) -> BatchHeader:
        return BatchHeader(
            signer_public_key=signer.get_public_key().as_hex(),
            transaction_ids=[txn.header_signature for txn in transactions],
        )

    @classmethod
    def _get_header_bytes(cls, signer: "Signer", transactions: List[Transaction]):
        return cls._get_header(signer, transactions).SerializeToString()

    @classmethod
    def _create_batch(cls, signer: "Signer", transactions: List[Transaction]) -> Batch:
        batch_header = cls._get_header_bytes(signer, transactions)
        signature = signer.sign(batch_header)
        return Batch(
            header=batch_header, header_signature=signature, transactions=transactions
        )

    @classmethod
    def create(cls, signer: "Signer", transactions: List[Transaction]) -> Batch:
        """Create signed Batch from list of transactions.

        Args:
            signer: Signer instance.
            transactions: List of Transaction instances.

        Returns:
            Batch instance.
        """
        return cls._create_batch(signer, transactions)

    @classmethod
    def create_encoded(cls, signer: "Signer", transactions: List[Transaction]) -> bytes:
        """Create encoded, signed Batch from list of transactions.

        Args:
            signer: Signer instance.
            transactions: List of Transaction instances.

        Returns:
            Bytes for Batch instance.
        """
        return cls.create(signer, transactions).SerializeToString()


class BatchListFactory:
    """Factory for creating BatchList."""

    @classmethod
    def _create_batch_list(cls, batches: List["Batch"]) -> BatchList:
        return BatchList(batches=batches)

    @classmethod
    def create(cls, batches: List["Batch"]) -> BatchList:
        """Create encoded BatchList.

        Args:
            batches: List of Batch instances.

        Returns:
            BatchList.
        """
        return cls._create_batch_list(batches)

    @classmethod
    def create_encoded(cls, batches: List["Batch"]) -> bytes:
        """Create encoded BatchList.

        Args:
            batches: List of Batch instances.

        Returns:
            Bytes for BatchList.
        """
        return cls.create(batches).SerializeToString()


class BlockTransactionFactory:
    @staticmethod
    def send(
        protos: List[Any],
        signer_key: "Secp256k1PrivateKey" = None,
        payload_type: PayloadFactory.Types = None,
    ) -> int:
        signer = CryptoFactory(swt.context).new_signer(signer_key)
        payloads = [
            PayloadFactory.create_encoded(
                payload_type, proto=proto, signer_key=signer_key
            )
            for proto in protos
        ]
        transactions = [
            TransactionFactory.create(signer, payload) for payload in payloads
        ]
        batch = BatchFactory.create(signer, transactions)
        batches = BatchListFactory.create_encoded([batch])
        return APIRequests.send_payload(batches)
