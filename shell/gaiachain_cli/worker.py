import copy
import logging
import random

import click
import time

from gaiachain_cli.agent import login
from gaiachain_cli.entity import (
    change_state,
    read as get_entities,
    create as generate_entities,
    get_ids as get_entities_ids,
    get_details as get_entity_details,
)
from gaiachain_cli.initial_data import agents as create_agents, agents_by_role

LOG = logging.getLogger(__name__)

ONE_HOUR_IN_SECONDS = 60 * 60
THREE_HOURS_IN_SECONDS = ONE_HOUR_IN_SECONDS * 3
EIGHT_HOURS_IN_SECONDS = ONE_HOUR_IN_SECONDS * 8


@click.command()
@click.pass_context
def worker(ctx):
    """Randomly generate events on chain."""

    LOG.info("Starting Gaiachain worker.")
    agents = copy.deepcopy(agents_by_role)
    ctx.invoke(create_agents)

    while True:
        action_fn = pick_action()
        done = action_fn(ctx, agents)
        if not done:
            LOG.info("Action failed.")
            continue

        wait_random_time()


def wait_random_time():
    wait_time_in_seconds = random.randint(
        THREE_HOURS_IN_SECONDS, EIGHT_HOURS_IN_SECONDS
    )
    hours = int(wait_time_in_seconds / ONE_HOUR_IN_SECONDS)
    minutes = int((wait_time_in_seconds % ONE_HOUR_IN_SECONDS) / 60)

    if hours > 1:
        hour_string = "{} hours".format(hours)
    elif hours == 1:
        hour_string = "1 hour"
    else:
        hour_string = ""

    if minutes > 1:
        minute_string = "{} minutes".format(minutes)
    elif minutes == 1:
        minute_string = "1 minute"
    else:
        minute_string = ""

    sleep_string = ", ".join([s for s in [hour_string, minute_string] if len(s) > 0])
    LOG.info("Sleep for {}.".format(sleep_string))
    time.sleep(wait_time_in_seconds)


def action_add_to_chain(ctx, agents):
    LOG.info("Action: add to chain")

    agent = agents["PRODUCER"]
    ctx.invoke(login, email=agent["email"], password=agent["password"])
    entities = ctx.invoke(get_entities)
    if not entities:
        LOG.info("No entities found, generate new.")
        entities = ctx.invoke(generate_entities, count=10, commodity_type="TIMBER")
        time.sleep(5)

    entity = random.choice(entities)
    LOG.debug("Selected entity: {}".format(entity["id"]))
    status = ctx.invoke(change_state, id=entity["id"], action="a")
    return status == 201


def action_move_item(ctx, agents):
    LOG.info("Action: move item")
    ids = ctx.invoke(get_entities_ids, only_active=True)
    if not ids:
        return False

    found = False
    entity = {}
    while not found:
        entity_id = random.choice(ids)
        entity = ctx.invoke(get_entity_details, entity_id)
        if entity["is_finished"]:
            ids = [id_ for id_ in ids if id_ != entity_id]
            if len(ids) == 0:
                return False
        else:
            found = True

    LOG.debug("Selected entity: {}".format(entity["id"]))

    owner_role = entity["owner"]["role"]
    status = entity["status"]
    if status == "ARRIVED":
        agent = agents[owner_role]
        action = "d"
    else:
        if owner_role == "PRODUCER":
            next_role = "LOG_PARK"
        elif owner_role == "LOG_PARK":
            next_role = "SAWMILL"
        elif owner_role == "SAWMILL":
            next_role = "EXPORTER"
        else:
            LOG.warning("Unknown next role")
            return False

        agent = agents[next_role]
        action = "a"

    ctx.invoke(login, email=agent["email"], password=agent["password"])
    status = ctx.invoke(change_state, id=entity["id"], action=action)
    return status == 201


def pick_action():
    # 10% for add new to chain
    # 90% for action in chain
    return random.choice([action_add_to_chain] + [action_move_item] * 9)
