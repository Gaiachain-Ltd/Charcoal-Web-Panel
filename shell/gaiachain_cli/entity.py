import logging

import click
import requests

from gaiachain_cli.utils import get_jwt

LOG = logging.getLogger(__name__)


@click.group()
def entity():
    """Entities requests."""
    pass


@entity.command()
@click.option("--commodity-type", "-t", default="TIMBER", type=str)
@click.option("--count", "-c", type=int, default=1)
@click.option("--jwt", "-j", type=str)
@click.pass_context
def create(ctx, commodity_type=None, count=1, jwt=None):
    """Create new entity."""
    if not jwt:
        jwt = get_jwt(ctx.obj["jwt_config_file"])
    if not jwt:
        LOG.warning("No JWT given, return.")
        return

    data = dict(commodity_type=commodity_type, count=count)
    r = requests.post(
        "{}/entities/uninitialized/".format(ctx.obj["url"]),
        json=data,
        headers={"Authorization": "Bearer {}".format(jwt)},
    )
    LOG.info("Create {} uninitialized entities. ".format(count))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    return r.json()


@entity.command()
@click.option("--id", "-i", type=str, required=True)
@click.option("--action", "-a", type=str, required=True)
@click.option("--jwt", "-j", type=str)
@click.pass_context
def change_state(ctx, id, action=None, jwt=None):
    """Change entity state."""
    if not jwt:
        jwt = get_jwt(ctx.obj["jwt_config_file"])
    if not jwt:
        LOG.warning("No JWT given, return.")
        return

    if action.lower() in ["a", "arrived"]:
        action = "ARRIVED"
    elif action.lower() in ["d", "departed"]:
        action = "DEPARTED"
    else:
        click.echo("Invalid action")
        return

    data = dict(action=action)
    r = requests.put(
        "{}/entities/{}/".format(ctx.obj["url"], id),
        json=data,
        headers={"Authorization": "Bearer {}".format(jwt)},
    )
    LOG.info("Put entity `{}` with action `{}`.".format(id, action))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    return r.status_code


@entity.command()
@click.option("--jwt", "-j", type=str)
@click.pass_context
def read(ctx, jwt):
    if not jwt:
        jwt = get_jwt(ctx.obj["jwt_config_file"])

    if not jwt:
        LOG.warning("No JWT given, return.")
        return

    r = requests.get(
        "{}/entities/uninitialized/".format(ctx.obj["url"]),
        headers={"Authorization": "Bearer {}".format(jwt)},
    )
    LOG.info("Get list of entities.")
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    return r.json()


@entity.command()
@click.pass_context
def get_ids(ctx, only_active=False):
    r = requests.get(
        "{}/entities/".format(ctx.obj["url"]), params={"only_active": only_active}
    )
    LOG.info("Get list of {} entities ids.".format("active" if only_active else "all"))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    return r.json()


@entity.command()
@click.pass_context
def get_details(ctx, entity_id):
    r = requests.get("{}/entities/{}/".format(ctx.obj["url"], entity_id))
    LOG.info("Get detail of entity `{}`".format(entity_id))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    return r.json()
