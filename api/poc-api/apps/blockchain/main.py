import sys

import argparse

from apps.blockchain.handlers.agent import AgentHandler
from apps.blockchain.handlers.entity import EntityHandler
from apps.blockchain.handlers.package import PackageHandler
from apps.blockchain.handlers.replantation import ReplantationHandler
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
        processor.add_handler(PackageHandler)
        processor.add_handler(ReplantationHandler)
        processor.start()
    except KeyboardInterrupt:
        pass



