import click
import helper as helper
import sys
from click_help_colors import HelpColorsCommand
import threading
import time
import requests
import docker

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
        helper.subprocess_cmd(command="docker-compose pull app")
        helper.subprocess_cmd(command="docker-compose pull phpfpm")

        if 'linux' in sys.platform:
            add_host_name_thread = threading.Thread(target=add_host_name)
            add_host_name_thread.start()

        if daemon:
            helper.subprocess_cmd(command="docker-compose up -d")
        else:
            helper.subprocess_cmd(command="docker-compose up")
    else:
        sys.exit(0)


def add_host_name():
    cli = helper.get_docker_client()
    container = helper.get_app_container()
    host_name = helper.get_host_name()
    if container and helper.is_valid_host_name(host_name):
        count = 1
        while True:
            if count == 10:
                return
            try:
                metadata = cli.inspect_container(container)
                if isinstance(metadata, dict):
                    if 'NetworkSettings' in metadata:
                        if 'IPAddress' in metadata['NetworkSettings']:
                            ipaddress = metadata['NetworkSettings']['IPAddress']
                            if helper.valid_ip(ipaddress):
                                helper.update_host(ipaddress, host_name)
                                return
            except requests.ReadTimeout:
                pass
            except docker.errors.NotFound:
                pass
            count += 1
            time.sleep(1)
