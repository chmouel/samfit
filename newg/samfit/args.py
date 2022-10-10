import click

tp_username_opt = click.option(
    "--username", "-u", help="TP Username", envvar="TP_USERNAME", required=True
)

tp_token_opt = click.option(
    "--token", help="TP Token", envvar="TP_TOKEN", required=True
)


@click.group()
@click.option("verbose", "--verbose", is_flag=True, help="Verbose output")
def cli(*_args, **_kwargs):
    """Samfit: a tool for fitting SAM models to data."""
    return _args, _kwargs


@cli.group("import")
@click.pass_context
def imports(*_args, **_kwargs):
    """Import data from various sources."""
    return _args, _kwargs
