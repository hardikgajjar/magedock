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

        if 'linux' in sys.platform:
            add_host_name()
    else:
        sys.exit(0)


def add_host_name():
    helper.warning_message('Adding hostname in /etc/hosts')
    cli = helper.get_docker_client()
    container = helper.get_php_container()
    host_name = helper.get_host_name()
    if container and helper.is_valid_host_name(host_name):
        metadata = cli.inspect_container(container)
        if isinstance(metadata, dict):
            if 'NetworkSettings' in metadata:
                ipaddress = metadata['NetworkSettings']['IPAddress']
                if helper.valid_ip(ipaddress):
                    if helper.host_exists(host_name):
                        helper.warning_message('Host ' + host_name + ' already exists in /etc/hosts file.')
                        if click.confirm('Do you want to replace it?'):
                            helper.update_host(ipaddress, host_name)
                    else:
                        helper.update_host(ipaddress, host_name)
