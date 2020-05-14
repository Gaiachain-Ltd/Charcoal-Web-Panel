import argparse
import sys

import pkg_resources
from sawtooth_sdk.processor.config import get_log_config
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.log import init_console_logging, log_configuration

from processor.handler import GaiachainTransactionHandler

DISTRIBUTION_NAME = "gaiachain"


def parse_args(args):
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-C", "--connect", help="Endpoint for the validator connection")

    parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        help="Increase output sent to stderr",
    )

    try:
        version = pkg_resources.get_distribution(DISTRIBUTION_NAME).version
    except pkg_resources.DistributionNotFound:
        version = "UNKNOWN"

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=(DISTRIBUTION_NAME + " (Hyperledger Sawtooth) version {}").format(
            version
        ),
        help="print version information",
    )

    return parser.parse_args(args)


def main(args=None):
    if args is None:
        args = sys.argv[1:]
    opts = parse_args(args)
    processor = None
    try:
        processor = TransactionProcessor(url=opts.connect or "tcp://validator:4004")
        log_config = get_log_config(filename="log_config.yaml")
        log_configuration(log_config=log_config)
        init_console_logging(verbose_level=opts.verbose)
        handler = GaiachainTransactionHandler()
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    finally:
        if processor is not None:
            processor.stop()


if __name__ == "__main__":
    main()
