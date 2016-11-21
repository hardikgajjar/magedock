import click
import helper as helper
import sys
import docker
import dockerpty
from click_help_colors import HelpColorsCommand


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green'
)
@click.option('--container', help='Container Name (Optional)')
def ssh(container):
    """SSH into container (PHP by default)"""
    if not container:
        docker_compose = helper.read_docker_compose()
        if docker_compose:
            container = docker_compose['phpfpm']['hostname'] + "_1"
        else:
            sys.exit(0)

    cli = helper.get_docker_client()

    if helper.docker_ping(cli):
        try:
            dockerpty.exec_command(cli, container, "bash")
        except docker.errors.APIError as err:
            helper.error_message("Docker error: {0}".format(err))
            helper.error_message("Make sure you have run 'magedock start' first.")
    else:
        helper.error_message("Can't ping to docker\nMake sure you have run 'magedock start' first")
