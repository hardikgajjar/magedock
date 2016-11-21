import click
from click_help_colors import HelpColorsGroup, HelpColorsCommand

from .commands.init import init
from .commands.start import start
from .commands.stop import stop
from .commands.ssh import ssh

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


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
