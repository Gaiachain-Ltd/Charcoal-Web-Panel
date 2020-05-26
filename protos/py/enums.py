import hashlib
from enum import Enum


class SimpleEnum(Enum):
    def __repr__(self):
        return self.value

    def __str__(self):
        return self.value

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif isinstance(other, self.value.__class__):
            return self.value == other
        return False

    def __len__(self):
        return len(self.value)

    def __get__(self, instance, owner):
        return self.value


class Gaiachain(SimpleEnum):
    FAMILY_NAME = "gaiachain"
    FAMILY_VERSION = "1.0"


class Namespaces(SimpleEnum):
    GA_NAMESPACE = hashlib.sha512("gaiachain".encode("utf-8")).hexdigest()[:6]
    AGENT = "ae"
    ENTITY = "e0"
    ENTITY_BATCH = "eb"
    PACKAGE = "pa"

    @staticmethod
    def get_prefix(subnamespace: str = ""):
        namespace = Namespaces.GA_NAMESPACE
        return namespace + subnamespace

    @staticmethod
    def get_address(name: str, subnamespace: str = "") -> str:
        prefix = Namespaces.get_prefix(subnamespace)
        length = -70 + len(prefix)
        encoded_name_end = hashlib.sha512(name.encode("utf-8")).hexdigest()[length:]
        return prefix + encoded_name_end


class Tbl(SimpleEnum):
    AGENTS = "agents"
    BLOCKS = "blocks"
    ENTITIES = "entities"
    ENTITY_BATCHES = "batches"
    ENTITY_EVENTS = "events"
    PACKAGES = "packages"
