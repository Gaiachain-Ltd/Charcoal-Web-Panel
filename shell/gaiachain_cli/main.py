#!/usr/bin/env python3
import os
import sys
import traceback
from logging.config import dictConfig

import click
import yaml
from sawtooth_cli.exceptions import CliException

from gaiachain_cli.agent import agent
from gaiachain_cli.entity import entity
from gaiachain_cli.initial_data import init
from gaiachain_cli.worker import worker

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS)
@click.pass_context
def gaiachain_cli(ctx):
    """Gaiachain CLI script"""
    pass


gaiachain_cli.add_command(agent)
gaiachain_cli.add_command(entity)
gaiachain_cli.add_command(init)
gaiachain_cli.add_command(worker)


def main_wrapper():
    # pylint: disable=bare-except

    path = "log_config.yaml"
    if os.path.exists(path):
        with open(path, "rt") as f:
            config = yaml.safe_load(f.read())
            dictConfig(config)
    else:
        print("Cannot find {} file, use default logger config".format(path))

    try:
        gaiachain_cli(
            obj={
                "url": "http://node1_server:5000/api/v1",
                "jwt_config_file": ".jwt.cfg",
            }
        )
    except CliException as e:
        print("Error: {}".format(e), file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    except BrokenPipeError:
        sys.stderr.close()
    except SystemExit as e:
        raise e
    except:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
