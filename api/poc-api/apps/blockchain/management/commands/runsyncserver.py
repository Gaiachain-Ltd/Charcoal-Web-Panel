# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.blockchain.handlers.agent import AgentHandler
from apps.blockchain.handlers.entity import EntityHandler
from apps.blockchain.handlers.package import PackageHandler
from apps.blockchain.handlers.replantation import ReplantationHandler
from apps.blockchain.processor import SyncProcessor


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument("-C", "--connect", help="Endpoint for the validator connection")

    def handle(self, *args, **options):
        try:
            processor = SyncProcessor(url=options['connect'])
            processor.add_handler(AgentHandler)
            processor.add_handler(EntityHandler)
            processor.add_handler(PackageHandler)
            processor.add_handler(ReplantationHandler)
            processor.start()
        except KeyboardInterrupt:
            pass
