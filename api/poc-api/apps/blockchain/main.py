import os
import sys
from logging.config import dictConfig

import argparse
import time
import yaml

from apps.blockchain.handlers.agent import AgentHandler
from apps.blockchain.handlers.entity import EntityHandler
from apps.blockchain.handlers.package import PackageHandler
from apps.blockchain.handlers.entity_batch import EntityBatchHandler
from apps.blockchain.processor import SyncProcessor


def parse_args(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-C", "--connect", help="Endpoint for the validator connection")

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    try:
        processor = SyncProcessor(url=opts.connect)
        processor.add_handler(AgentHandler)
        processor.add_handler(EntityHandler)
        processor.add_handler(EntityBatchHandler)
        processor.add_handler(PackageHandler)
        processor.start()
    except KeyboardInterrupt:
        pass



