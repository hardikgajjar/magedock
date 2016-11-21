import click
import os
import subprocess
import sys
from docker.client import Client
from docker.utils import kwargs_from_env
import socket
import yaml


def normal_message(text):
    click.secho(text)


def success_message(text):
    click.secho(text, fg='green')


def error_message(text):
    click.secho(text, fg='red')


def warning_message(text):
    click.secho(text, fg='yellow')


def start_dinghy_if_required():
    cli = get_docker_client()
    if not docker_ping(cli):
        if sys.platform == "darwin":
            dinghy_ip = subprocess_cmd(command="dinghy ip", print_lines=False)
            if not valid_ip(dinghy_ip):
                subprocess_cmd(command="dinghy start")
            subprocess_cmd(command="$(dinghy shellinit)", write_env=True, print_lines=False)


def get_docker_client():
    kwargs = kwargs_from_env()
    kwargs['tls'].assert_hostname = False
    kwargs['version'] = '1.22'
    kwargs['timeout'] = 3
    return Client(**kwargs)


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


def docker_ping(cli):
    try:
        cli.ping()
        return True
    except:
        return False


def subprocess_cmd(command, write_env=False, print_lines=True):
    process = subprocess.Popen(["sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(command + "\n")

    if write_env:
        process.stdin.write("env\n")

    process.stdin.close()

    response = ''

    while True:
        line = process.stdout.readline()
        if print_lines:
            click.echo(line.strip())
        if write_env:
            if "=" in line.strip():
                name, value = line.strip().split("=", 1)
                os.environ[name] = value
        response += line.strip()

        if not line and process.poll() is not None:
            break

    return response


def read_docker_compose():
    try:
        f = open('docker-compose.yml')
        dataMap = yaml.safe_load(f)
        f.close()
        return dataMap
    except:
        error_message("File not found: docker-compose.yml\nmake sure you're in project directory.")
        return False