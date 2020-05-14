from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from apps.users.managers import UserManager
from apps.blockchain.transaction import PayloadFactory, BlockTransactionFactory
from apps.blockchain.sawtooth import swt
from protos.agent_pb2 import Agent


class User(AbstractUser):
    username = None
    email = models.EmailField(verbose_name=_('email address'), unique=True)
    role = models.ForeignKey(
        'users.Role', verbose_name=_('Role'), related_name='users', on_delete=models.CASCADE, null=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

    private_key_str = models.CharField(max_length=128, blank=True)
    public_key = models.CharField(max_length=128, blank=True)

    @property
    def private_key(self):
        return Secp256k1PrivateKey.from_hex(
            self.private_key_str
        )

    @property
    def is_director(self):
        return self.role is not None and self.role.name == 'DIRECTOR'

    @property
    def is_logger(self):
        return self.role is not None and self.role.name == 'LOGGER'

    @property
    def is_carbonizer(self):
        return self.role is not None and self.role.name == 'CARBONIZER'

    def save(self, *args, **kwargs):
        superuser_role, _ = Role.objects.get_or_create(name='SUPER_USER')
        if self.is_superuser and not self.role:
            self.role = superuser_role
        elif not self.is_superuser and self.role == superuser_role:
            self.role = None

        if not self.private_key_str:
            private_key = swt.context.new_random_private_key()
            self.private_key_str = private_key.as_hex()
            self.public_key = swt.context.get_public_key(private_key).as_hex()

        super().save(*args, **kwargs)

    def get_proto(self):
        return self._build_proto()

    def _build_proto(self):
        proto = Agent(
            email=self.email,
            role=getattr(Agent, self.role.name),
            public_key=self.public_key,
        )
        return proto

    def add_to_chain(self):
        return BlockTransactionFactory.send(
            protos=[self._build_proto()],
            signer_key=self.private_key,
            payload_type=PayloadFactory.Types.CREATE_AGENT,
        )


class Role(models.Model):
    name = models.CharField(verbose_name=_('Role name'), max_length=100)

    def __str__(self):
        return self.name
