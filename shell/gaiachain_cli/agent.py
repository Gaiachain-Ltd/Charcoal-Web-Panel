import logging

import click
import requests

from gaiachain_cli.utils import save_jwt

LOG = logging.getLogger(__name__)


@click.group()
def agent():
    """Agent requests."""
    pass


@agent.command()
@click.option("--email", "-e", required=True, type=str)
@click.option("--company_name", "-c", type=str, default="Test Inc.")
@click.option("--role", "-r", type=str, default="PRODUCER")
@click.option("--password", "-p", type=str, default="test1234")
@click.option("--lat", type=float, default=1.0)
@click.option("--long", type=float, default=1.0)
@click.pass_context
def create(
    ctx, email=None, company_name=None, role=None, password=None, lat=None, long=None
):
    """Create new agent."""
    data = dict(
        company_name=company_name,
        email=email,
        role=role,
        password=password,
        location=[lat, long],
    )
    r = requests.post("{}/auth/register/".format(ctx.obj["url"]), json=data)
    LOG.info("Create `{}` agent. ".format(data["email"]))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    try:
        jwt = r.json()["token"]
    except:
        pass
    else:
        save_jwt(ctx.obj["jwt_config_file"], jwt)


@agent.command()
@click.option("--email", "-e", type=str, required=True)
@click.option("--password", "-p", type=str, default="test1234")
@click.pass_context
def login(ctx, email=None, password=None):
    data = dict(email=email, password=password)
    r = requests.post("{}/auth/login/".format(ctx.obj["url"]), json=data)
    LOG.info("Authenticate user `{}`. ".format(email))
    LOG.debug("Status: `{}`".format(r.status_code))
    LOG.debug("Response: `{}`".format(r.json()))
    try:
        jwt = r.json()["token"]
    except:
        pass
    else:
        save_jwt(ctx.obj["jwt_config_file"], jwt)
