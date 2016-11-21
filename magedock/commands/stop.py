import click
import helper as helper
import sys
from click_help_colors import HelpColorsCommand


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green'
)
def stop():
    """Stop Project"""
    docker_compose = helper.read_docker_compose()
    if docker_compose:
        # start dinghy if not started
        helper.start_dinghy_if_required()

        helper.subprocess_cmd(command="docker-compose stop")
    else:
        sys.exit(0)
