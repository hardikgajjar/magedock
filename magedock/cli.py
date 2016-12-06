import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand

from .commands.init import init
from .commands.start import start
from .commands.stop import stop
from .commands.ssh import ssh
from .commands.db import db
import pkg_resources  # part of setuptools


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.secho(pkg_resources.require("magedock")[0].version, fg='green')
    ctx.exit()


@click.option('-v', '--version', is_flag=True, callback=print_version,
              expose_value=False, is_eager=True)
@click.group(
    cls=HelpColorsGroup,
    help_headers_color='yellow',
    help_options_color='green',
    context_settings=CONTEXT_SETTINGS
)
def main():
    pass


main.add_command(init)
main.add_command(ssh)
main.add_command(start)
main.add_command(stop)
main.add_command(db)
