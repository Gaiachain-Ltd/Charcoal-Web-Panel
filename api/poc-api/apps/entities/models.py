from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _

from apps.additional_data.models import OvenType
from apps.blockchain.transaction import PayloadFactory, BlockTransactionFactory

from protos.entity_pb2 import Entity as EntityProto, Package as PackageProto, Replantation as ReplantationProto


class Entity(models.Model):
    INITIAL = 'IN'
    LOGGING_BEGINNING = 'LB'
    LOGGING_ENDING = 'LE'
    CARBONIZATION_BEGINNING = 'CB'
    CARBONIZATION_ENDING = 'CE'
    LOADING_TRANSPORT = 'TR'
    RECEPTION = 'RE'
    ACTIONS = [
        (INITIAL, 'Initial'),
        (LOGGING_BEGINNING, 'Logging Beginning'),
        (LOGGING_ENDING, 'Logging Ending'),
        (CARBONIZATION_BEGINNING, 'Carbonization Beginning'),
        (CARBONIZATION_ENDING, 'Carbonization Ending'),
        (LOADING_TRANSPORT, 'Loading & Transport'),
        (RECEPTION, 'Reception')
    ]
    CHILD_MODEL_NAMES = {
        LOGGING_BEGINNING: 'loggingbeginning',
        LOGGING_ENDING: 'loggingending',
        CARBONIZATION_BEGINNING: 'carbonizationbeginning',
        CARBONIZATION_ENDING: 'carbonizationending',
        LOADING_TRANSPORT: 'loadingtransport',
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
    blockchain_batch_id = models.CharField(verbose_name=_('Blockchain Batch ID'), blank=True, max_length=128)

    def __str__(self):
        if self.package:
            return "{}-{}-{}-{}".format(self.package.pid, self.action, self.timestamp, self.user)
        return "{}-{}-{}".format(self.action, self.timestamp, self.user)

    def web_description(self):
        try:
            return getattr(self, self.CHILD_MODEL_NAMES[self.action]).web_description
        except:
            return _('Entity not found')

    def build_proto(self):
        return EntityProto(**{
            'status': getattr(self, self.CHILD_MODEL_NAMES[self.action]).get_proto_status(),
            'timestamp': self.timestamp,
            'location': {
                'lat': self.location.y,
                'long': self.location.x,
            },
            'user': self.user.get_proto(),
            **getattr(self, self.CHILD_MODEL_NAMES[self.action]).get_proto_data()
        })

    def add_to_chain(self, package_type, status, payload_type, **kwargs):
        proto = self._build_proto(package_type, status, **kwargs)
        BlockTransactionFactory.send(
            protos=[proto],
            signer_key=self.user.private_key,
            payload_type=payload_type,
        )
        return self

    def update_in_chain(self):
        """
            Update Package entities.
        """
        self.package.update_in_chain(self)

    class Meta:
        ordering = ('-timestamp',)


class Package(models.Model):
    PLOT = 'PLT'
    HARVEST = 'HAR'
    TRUCK = 'TRK'

    PACKAGES = [
        (PLOT, 'Plot'),
        (HARVEST, 'Harvest'),
        (TRUCK, 'Transport'),
    ]
    pid = models.CharField(verbose_name=_('Pid'), null=True, max_length=100)
    type = models.CharField(verbose_name=_('Type'), choices=PACKAGES, default=PLOT, max_length=30)
    last_action = models.OneToOneField(
        'entities.Entity', verbose_name=_('Last action'), on_delete=models.CASCADE,
        null=True, blank=True, related_name='package_last_action'
    )

    plot = models.OneToOneField(
        'entities.Package', verbose_name='Plot ID', related_name='plot_harvest',
        on_delete=models.CASCADE, null=True, blank=True
    )
    harvest = models.ForeignKey(
        'entities.Package', verbose_name='Harvest ID', related_name='trucks',
        on_delete=models.CASCADE, null=True, blank=True
    )

    def __str__(self):
        try:
            return self.pid or ''
        except AttributeError:
            return str(self.id)

    def _build_proto(self, package_type, **kwargs):
        """Build package proto.

        Returns:
            Package proto.
        """
        proto_kwargs = {
            'id': self.pid,
            'type': package_type,
            'entities': [x.build_proto() for x in self.package_entities.all()]
        }
        if self.plot:
            proto_kwargs['plot'] = PackageProto(id=self.plot.pid)
        if self.harvest:
            proto_kwargs['harvest'] = PackageProto(id=self.harvest.pid)
        proto = PackageProto(**proto_kwargs)
        return proto

    def add_to_chain(self, user, package_type, payload_type, **kwargs):
        proto = self._build_proto(package_type, **kwargs)
        response = BlockTransactionFactory.send(
            protos=[proto],
            signer_key=user.private_key,
            payload_type=payload_type,
        )
        self.assign_batch_id(response, self.package_entities.all())
        return self

    def update_in_chain(self, entity):
        """
            Update Package entities.
        """
        data = {
            'id': self.pid,
            'entity': entity.build_proto()
        }
        response = BlockTransactionFactory.send(
            protos=[data],
            signer_key=entity.user.private_key,
            payload_type=PayloadFactory.Types.UPDATE_PACKAGE,
        )
        self.assign_batch_id(response, [entity])
        return response

    def assign_batch_id(self, response, entities):
        if 'link' in response:
            batch_id = response['link'].split('=')[1]
            for entity in entities:
                entity.blockchain_batch_id = batch_id
                entity.save()


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

    def get_proto_status(self):
        return EntityProto.LOGGING_BEGINNING

    def get_proto_data(self):
        return {
            'parcel': str(self.parcel),
            'beginning_date': self.beginning_date,
            'village': str(self.village),
            'tree_specie': str(self.tree_specie)
        }

    @property
    def short_description(self):
        return _("Logging beginning | Plot ID created.")

    @property
    def web_description(self):
        return _('Logging has begun')


class LoggingEnding(ActionAbstract):
    ending_date = models.PositiveIntegerField(verbose_name=_('Ending date'))
    number_of_trees = models.PositiveSmallIntegerField(verbose_name=_('Number of trees'))

    @property
    def short_description(self):
        return _("Logging ending | Plot ID updated.")

    @property
    def web_description(self):
        return _('Logging has ended')

    def get_proto_status(self):
        return EntityProto.LOGGING_ENDING

    def get_proto_data(self):
        return {
            'ending_date': self.ending_date,
            'number_of_trees': self.number_of_trees,
        }


class Oven(models.Model):
    oven_id = models.CharField(max_length=1, verbose_name=_('Oven ID'))
    carbonization_ending = models.ForeignKey(
        'entities.CarbonizationEnding', verbose_name=_('Carbonization Ending'),
        on_delete=models.CASCADE, null=True, related_name='ovens'
    )


class CarbonizationBeginning(ActionAbstract):
    oven = models.OneToOneField(
        Oven, verbose_name=_('Oven'),
        related_name='carbonization_beginning', on_delete=models.CASCADE
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

    @property
    def web_description(self):
        return _(f'Oven {self.oven.oven_id} - Carbonization has begun')

    def get_proto_status(self):
        return EntityProto.CARBONIZATION_BEGINNING

    @property
    def oven_measurements(self):
        if self.oven_height and self.oven_length and self.oven_width:
            return {
                'oven_height': self.oven_height,
                'oven_width': self.oven_width,
                'oven_length': self.oven_length,
            }
        else:
            return OvenType.objects.filter(id=self.oven_type_id).values('oven_height', 'oven_width', 'oven_length')[0]

    def get_proto_data(self):
        proto_data = {
            'beginning_date': self.beginning_date,
            'oven': self.oven.oven_id,
            'oven_type': str(self.oven_type),
        }
        proto_data.update(**self.oven_measurements)
        return proto_data

    def add_to_chain(self, *args):
        if self.entity.package.package_entities.count() == 1:
            return self.entity.package.add_to_chain(*args)
        return self.entity.update_in_chain()


class CarbonizationEnding(ActionAbstract):
    end_date = models.PositiveIntegerField(verbose_name=_('End date'))

    @property
    def short_description(self):
        return _("Carbonization ending | Harvest ID updated.")

    @property
    def web_description(self):
        ovens_ids = ', '.join(list(self.ovens.values_list('oven_id', flat=True)))
        return _(f'Oven{"s" if self.ovens.count() > 1 else ""} {ovens_ids} - Carbonization has ended')

    def get_proto_status(self):
        return EntityProto.CARBONIZATION_ENDING

    def get_proto_data(self):
        return {
            'end_date': self.end_date,
            'ovens': list(self.ovens.values_list('oven_id', flat=True))
        }


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
    plate_number = models.CharField(max_length=16, verbose_name=_('Truck ID'))
    loading_date = models.PositiveIntegerField(verbose_name=_('Loading date'))
    destination = models.ForeignKey(
        'additional_data.Destination', verbose_name=_('Destination'), on_delete=models.CASCADE,
        related_name='transports', null=True, blank=True
    )

    @property
    def web_description(self):
        return _(f'Bags have been loaded on truck {self.plate_number}')

    def get_proto_status(self):
        return EntityProto.LOADING_TRANSPORT

    def get_proto_data(self):
        return {
            'destination': str(self.destination),
            'loading_date': self.loading_date,
            'plate_number': self.plate_number,
            'bags': list(self.bags.values_list('qr_code', flat=True))
        }

    @property
    def short_description(self):
        return _("Transport created | Truck ID created.")


class ReceptionImage(models.Model):
    DOCUMENT = 'document'
    RECEIPT = 'receipt'
    TYPE_CHOICES = (
        (DOCUMENT, 'Document'),
        (RECEIPT, 'Receipt'),
    )
    type = models.CharField(verbose_name=_('Type'), max_length=8, choices=TYPE_CHOICES)
    image = models.ImageField(verbose_name='Image', upload_to='photos/%Y/%m/%d')
    reception = models.ForeignKey(
        'entities.Reception', verbose_name=_('Reception'),
        on_delete=models.CASCADE, related_name='images'
    )


class Reception(ActionAbstract):
    reception_date = models.PositiveIntegerField(verbose_name=_('Reception date'), null=True)

    def get_proto_status(self):
        return EntityProto.RECEPTION

    def get_proto_data(self):
        return {
            'documents_photos': list(self.images.filter(type=ReceptionImage.DOCUMENT).values_list('image', flat=True)),
            'receipt_photos': list(self.images.filter(type=ReceptionImage.RECEIPT).values_list('image', flat=True)),
            'bags': list(self.bags.values_list('qr_code', flat=True))
        }

    @property
    def short_description(self):
        return _("Received at the reception")

    @property
    def web_description(self):
        return _('Reception at storage facility')


class Replantation(models.Model):
    plot = models.OneToOneField(
        'entities.Package', on_delete=models.CASCADE, verbose_name=_('Plot ID'),
        related_name='replantation'
    )
    trees_planted = models.PositiveIntegerField(verbose_name=_('Number of trees planted'))
    tree_specie = models.ForeignKey(
        'additional_data.TreeSpecie', on_delete=models.CASCADE, verbose_name=_('Tree specie')
    )
    user = models.ForeignKey(
        'users.User', verbose_name=_('User'), on_delete=models.CASCADE,
        related_name='replantations'
    )
    beginning_date = models.PositiveIntegerField(verbose_name=_('Beginning date'))
    ending_date = models.PositiveIntegerField(verbose_name=_('Ending date'))
    location = models.PointField(verbose_name=_('Location'))
    blockchain_batch_id = models.CharField(verbose_name=_('Blockchain Batch ID'), blank=True, max_length=128)

    def _build_proto(self):
        return ReplantationProto(**{
            'id': self.id,
            'beginning_date': self.beginning_date,
            'ending_date': self.ending_date,
            'trees_planted': self.trees_planted,
            'tree_specie': str(self.tree_specie),
            'plot': PackageProto(id=self.plot.pid),
            'location': {
                'lat': self.location.y,
                'long': self.location.x,
            },
            'user': self.user.get_proto(),
        })

    def add_to_chain(self, payload_type):
        proto = self._build_proto()
        response = BlockTransactionFactory.send(
            protos=[proto],
            signer_key=self.user.private_key,
            payload_type=payload_type,
        )
        self.assign_batch_id(response)
        return self

    def assign_batch_id(self, response):
        if 'link' in response:
            batch_id = response['link'].split('=')[1]
            self.blockchain_batch_id = batch_id
            self.save()