from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from apps.entities.utils import unix_to_datetime_tz
from apps.blockchain.transaction import PayloadFactory, BlockTransactionFactory

from protos.entity_pb2 import Entity as EntityProto


class Entity(models.Model):
    INITIAL = 'IN'
    LOGGING_BEGINNING = 'LB'
    LOGGING_ENDING = 'LE'
    CARBONIZATION_BEGINNING = 'CB'
    CARBONIZATION_ENDING = 'CE'
    LOADING_TRANSPORT = 'TR'
    CHECKPOINT_FOREST = 'CF'
    CHECKPOINT_SODEFOR = 'CS'
    RECEPTION = 'RE'
    ACTIONS = [
        (INITIAL, 'Initial'),
        (LOGGING_BEGINNING, 'Logging Beginning'),
        (LOGGING_ENDING, 'Logging Ending'),
        (CARBONIZATION_BEGINNING, 'Carbonization Beginning'),
        (CARBONIZATION_ENDING, 'Carbonization Ending'),
        (LOADING_TRANSPORT, 'Loading & Transport'),
        (CHECKPOINT_FOREST, 'Checkpoint Eaux Et Forest'),
        (CHECKPOINT_SODEFOR, 'Checkpoint Sodefor'),
        (RECEPTION, 'Reception')
    ]
    CHILD_MODEL_NAMES = {
        LOGGING_BEGINNING: 'loggingbeginning',
        LOGGING_ENDING: 'loggingending',
        CARBONIZATION_BEGINNING: 'carbonizationbeginning',
        CARBONIZATION_ENDING: 'carbonizationending',
        LOADING_TRANSPORT: 'loadingtransport',
        CHECKPOINT_FOREST: 'checkpoint',
        CHECKPOINT_SODEFOR: 'checkpoint',
        RECEPTION: 'reception',
    }

    timestamp = models.PositiveIntegerField(verbose_name=_('Timestamp'))
    action = models.CharField(verbose_name=_('Action'), choices=ACTIONS, default=INITIAL, max_length=30)
    user = models.ForeignKey(
        'users.User', verbose_name=_('User'), null=True, blank=True, on_delete=models.CASCADE,
        related_name='entities'
    )
    package = models.ForeignKey(
        'entities.Package', verbose_name=_('Package'), on_delete=models.CASCADE,
        related_name='package_entities', null=True
    )
    location = models.PointField(verbose_name=_('Location'), null=True, blank=True)

    def __str__(self):
        if self.package:
            return "{}-{}-{}-{}".format(self.package.pid, self.action, self.timestamp, self.user)
        return "{}-{}-{}".format(self.action, self.timestamp, self.user)

    def _build_proto(self, package_type, status, **kwargs):
        """Build entity proto.

        Returns:
            Entity proto.
        """
        proto_kwargs = {
            'id': str(self.package.pid),
            'package_type': package_type,
            'status': status,
            'location': {
                'lat': self.location.y,
                'long': self.location.x,
            },
            'user': self.user.get_proto(),
        }
        if status == EntityProto.HARVESTING:
            proto_kwargs['parcel'] = kwargs.pop('parcel')
            proto_kwargs['harvest_date'] = kwargs.pop('harvest_date')
        elif status == EntityProto.BAGGING:
            proto_kwargs['entities'] = [EntityProto(id=k, weight=int(v)) for k, v in kwargs.pop('harvest_data').items()]
        elif status == EntityProto.LOT_CREATION:
            proto_kwargs['entities'] = [
                EntityProto(id=sac_id) for sac_id in self.package.package_sacs.values_list('pid', flat=True)
            ]
            proto_kwargs['notes'] = kwargs.pop('notes')
        proto = EntityProto(**proto_kwargs)
        return proto

    def add_to_chain(self, package_type, status, payload_type, **kwargs):
        proto = self._build_proto(package_type, status, **kwargs)
        BlockTransactionFactory.send(
            protos=[proto],
            signer_key=self.user.private_key,
            payload_type=payload_type,
        )
        return self

    def update_in_chain(self, new_state, data):
        """
            Update Entity state.
        """
        data.update({
            'id': self.package.pid,
            'status': new_state,
            'user': self.user.get_proto()
        })
        return BlockTransactionFactory.send(
            protos=[data],
            signer_key=self.user.private_key,
            payload_type=PayloadFactory.Types.UPDATE_ENTITY,
        )

    class Meta:
        ordering = ('-timestamp',)


class Package(models.Model):
    PLOT = 'PLT'
    HARVEST = 'HAR'
    TRUCK = 'TRK'

    PACKAGES = [
        (PLOT, 'Plot'),
        (HARVEST, 'Harvest'),
        (TRUCK, 'Truck'),
    ]
    pid = models.CharField(verbose_name=_('Pid'), null=True, max_length=50)
    type = models.CharField(verbose_name=_('Type'), choices=PACKAGES, default=PLOT, max_length=30)
    last_action = models.OneToOneField(
        'entities.Entity', verbose_name=_('Last action'), on_delete=models.CASCADE,
        null=True, blank=True, related_name='package_last_action'
    )

    def __str__(self):
        try:
            return self.pid or ''
        except AttributeError:
            return str(self.id)


class ActionAbstract(models.Model):
    entity = models.OneToOneField(
        'entities.Entity', verbose_name=_('Entity'), on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True

    def __str__(self):
        try:
            return self.entity.package.pid
        except AttributeError:
            return str(self.id)


class LoggingBeginning(ActionAbstract):
    parcel = models.ForeignKey(
        'additional_data.Parcel', verbose_name=_('Parcel'), on_delete=models.CASCADE,
        related_name='parcel_loggings', null=True
    )
    village = models.ForeignKey(
        'additional_data.Village', verbose_name=_('Village'), related_name='loggings',
        null=True, on_delete=models.SET_NULL
    )
    tree_specie = models.ForeignKey(
        'additional_data.TreeSpecie', verbose_name=_('Tree Specie'), related_name='loggings',
        null=True, on_delete=models.SET_NULL
    )
    beginning_date = models.PositiveIntegerField(verbose_name=_('Beginning date'))

    # def add_to_chain(self):
    #     return self.entity.add_to_chain(
    #         EntityProto.HARVEST, EntityProto.HARVESTING, PayloadFactory.Types.CREATE_ENTITY,
    #         parcel=str(self.parcel), harvest_date=self.harvest_date
    #     )

    @property
    def short_description(self):
        return _("Logging beginning | Plot ID created.")


class LoggingEnding(ActionAbstract):
    ending_date = models.PositiveIntegerField(verbose_name=_('Ending date'))
    number_of_trees = models.PositiveSmallIntegerField(verbose_name=_('Number of trees'))

    @property
    def short_description(self):
        return _("Logging ending | Plot ID updated.")

    # def update_in_chain(self):
    #     data = {
    #         'transporter': str(self.transporter),
    #         'transport_date': self.transport_date or 0,
    #         'destination': str(self.destination),
    #     }
    #     return self.entity.update_in_chain(EntityProto.WAREHOUSE_TRANSPORT, data)


class Oven(models.Model):
    oven_id = models.CharField(max_length=1, verbose_name=_('Oven ID'))


class CarbonizationBeginning(ActionAbstract):
    oven = models.OneToOneField(
        Oven, verbose_name=_('Oven'),
        related_name='carbonization_beginning', on_delete=models.CASCADE
    )
    plot = models.ForeignKey(
        Package, verbose_name='Plot ID', related_name='carbonization_beginnings',
        on_delete=models.CASCADE
    )
    beginning_date = models.PositiveIntegerField(verbose_name=_('Beginning date'))
    oven_type = models.ForeignKey(
        'additional_data.OvenType', verbose_name=_('Oven type'),
        related_name='carbonization_beginnings', on_delete=models.CASCADE
    )
    oven_height = models.PositiveIntegerField(verbose_name=_('Oven height'), null=True, blank=True)
    oven_width = models.PositiveIntegerField(verbose_name=_('Oven width'), null=True, blank=True)
    oven_length = models.PositiveIntegerField(verbose_name=_('Oven length'), null=True, blank=True)

    @property
    def short_description(self):
        return _("Carbonization beginning | Oven ID created. Harvest ID created.")

    # def add_to_chain(self):
    #     return self.entity.add_to_chain(
    #         EntityProto.HARVEST, EntityProto.HARVESTING, PayloadFactory.Types.CREATE_ENTITY,
    #         parcel=str(self.parcel), harvest_date=self.harvest_date
    #     )


class CarbonizationEnding(ActionAbstract):
    ovens = models.ManyToManyField(Oven, verbose_name=_('Ovens'), related_name='carbonization_endings')
    end_date = models.PositiveIntegerField(verbose_name=_('End date'))
    harvest = models.ForeignKey(
        Package, verbose_name=_('Harvest'), related_name='carbonization_endings',
        null=True, on_delete=models.SET_NULL
    )

    @property
    def short_description(self):
        return _("Carbonization ending | Harvest ID updated.")

    # def update_in_chain(self):
    #     data = {
    #         'transporter': str(self.transporter),
    #         'transport_date': self.transport_date or 0,
    #         'destination': str(self.destination),
    #     }
    #     return self.entity.update_in_chain(EntityProto.WAREHOUSE_TRANSPORT, data)


class Bag(models.Model):
    pid = models.CharField(verbose_name=_('Pid'), null=True, max_length=50)
    qr_code = models.CharField(verbose_name=_('QR Code'), null=True, blank=True, max_length=14)
    transport = models.ForeignKey(
        'entities.LoadingTransport', verbose_name=_('Transport ID'), on_delete=models.CASCADE,
        related_name='bags', null=True
    )
    reception = models.ForeignKey(
        'entities.Reception', verbose_name=_('Reception'), on_delete=models.CASCADE,
        related_name='bags', null=True, blank=True
    )


class LoadingTransport(ActionAbstract):
    harvest = models.ForeignKey(
        'entities.Package', verbose_name=_('Harvest ID'), on_delete=models.CASCADE,
        related_name='transports', null=True
    )
    truck_id = models.CharField(max_length=16, verbose_name=_('Truck ID'))
    loading_date = models.PositiveIntegerField(verbose_name=_('Loading date'))
    destination = models.ForeignKey(
        'additional_data.Destination', verbose_name=_('Destination'), on_delete=models.CASCADE,
        related_name='transports', null=True, blank=True
    )

    def update_in_chain(self):
        data = {
            'transporter': str(self.transporter),
            'transport_date': self.transport_date or 0,
            'destination': str(self.destination),
        }
        return self.entity.update_in_chain(EntityProto.WAREHOUSE_TRANSPORT, data)

    @property
    def short_description(self):
        return _("Transport created | Truck ID created.")


class Checkpoint(ActionAbstract):
    qr_code = models.CharField(verbose_name=_('QR Code'), null=True, blank=True, max_length=14)
    photo = models.ImageField(verbose_name='Photo of document')

    @property
    def short_description(self):
        return _("Checkpoint created | Truck ID updated.")


class Reception(ActionAbstract):
    documents_photo = models.ImageField(verbose_name='Photo of documents', null=True)
    receipt_photo = models.ImageField(verbose_name='Photo of receipt', null=True)

    def update_in_chain(self):
        data = {
            'reception_date': self.reception_date,
            'transport_date': self.transport_date or 0,
            'buyer': str(self.buyer)
        }
        return self.entity.update_in_chain(EntityProto.SECTION_RECEPTION, data)

    @property
    def short_description(self):
        return _("Received at the reception")
