import os
import sys
from logging.config import dictConfig

import argparse
import rethinkdb as r
import time
import yaml

from sync.handlers.agent import AgentHandler
from sync.handlers.entity import EntityHandler
from sync.handlers.entity_batch import EntityBatchHandler
from sync.processor import SyncProcessor


def configure_logger():
    path = "log_config.yaml"
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
            dictConfig(config)
    else:
        print("Cannot find {} file, use default logger config".format(path))


def configure_db():
    r.connect(
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", 28015),
        db="gaiachain",
    ).repl()


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
        processor.start()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    time.sleep(15)
    configure_logger()
    configure_db()
    main()
