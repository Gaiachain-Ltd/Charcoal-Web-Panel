import click

from gaiachain_cli.agent import create as create_agent, login
from gaiachain_cli.entity import create as create_entity


@click.group()
def init():
    """Generate initial data."""
    pass


agents_by_role = {
    "PRODUCER": dict(
        company_name="Woodcutter Inc.",
        email="producer@gaiachain.io",
        role="PRODUCER",
        password="test1234",
        lat=5.534660,
        long=-9.507254,
    ),
    "LOG_PARK": dict(
        company_name="Log Park Inc.",
        email="logpark@gaiachain.io",
        role="LOG_PARK",
        password="test1234",
        lat=5.508764,
        long=-9.507045,
    ),
    "SAWMILL": dict(
        company_name="Sawmill Inc.",
        email="sawmill@gaiachain.io",
        role="SAWMILL",
        password="test1234",
        lat=5.480245,
        long=-9.537423,
    ),
    "EXPORTER": dict(
        company_name="Tree Exp",
        email="exporter@gaiachain.io",
        role="EXPORTER",
        password="test1234",
        lat=5.468805,
        long=-9.577706,
    ),
}

agents_data = [
    agents_by_role["PRODUCER"],
    agents_by_role["LOG_PARK"],
    agents_by_role["SAWMILL"],
    agents_by_role["EXPORTER"],
]


@init.command()
@click.pass_context
def agents(ctx):
    """Generate initial agents."""
    for data in agents_data:
        ctx.invoke(create_agent, **data)


@init.command()
@click.pass_context
def entities(ctx):
    for data in agents_data:
        if data["role"] == "PRODUCER":
            ctx.invoke(login, email=data["email"], password=data["password"])
            return ctx.invoke(create_entity, count=10, commodity_type="TIMBER")
