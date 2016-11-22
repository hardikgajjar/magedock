import click
import helper as helper
import sys
from click_help_colors import HelpColorsCommand


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green'
)
@click.option('-d', '--daemon', is_flag=True, help='Daemon mode')
def start(daemon):
    """Start Project"""
    docker_compose = helper.read_docker_compose()
    if docker_compose:
        # start dinghy if not started
        helper.start_dinghy_if_required()

        helper.warning_message('Downloading latest images')
        helper.subprocess_cmd(command="docker-compose pull")

        if daemon:
            helper.subprocess_cmd(command="docker-compose up -d")
        else:
            helper.subprocess_cmd(command="docker-compose up")
    else:
        sys.exit(0)
