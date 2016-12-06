import click
import os
import subprocess
import sys
from docker.client import Client
from docker.utils import kwargs_from_env
import socket
import yaml
import re


def normal_message(text):
    click.secho(text)


def success_message(text):
    click.secho(text, fg='green')


def error_message(text):
    click.secho(text, fg='red')


def warning_message(text, nl=True):
    click.secho(text, fg='yellow', nl=nl)


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
    if 'tls' in kwargs:
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


def is_valid_host_name(hostname):
    """
    First it checks to see if the hostname is too long. Next, it checks to see if the first character is a number.
    If the last character is a ".", it is removed. A list of acceptable characters is then compiled and each section
    of the host name, split by any ".", is checked for valid characters. If there everything is valid, True is returned.
    """
    if len(hostname) > 255:
        return False
    if hostname[0].isdigit(): return False
    if hostname[-1:] == ".":
        hostname = hostname[:-1] # strip exactly one dot from the right, if present
    allowed = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
    return all(allowed.match(x) for x in hostname.split("."))


def update_host(ipaddress, hostname):
    """
    The update function takes the ip address and hostname passed into the function and adds it to the host file.
    """
    if not 'linux' in sys.platform:
        error_message('Host update is only required in linux systems')
        return False

    filename = '/etc/hosts'
    tmp_filename = '/tmp/hosts.tmp'

    original = open(filename, 'rt')
    contents = original.read() + "\n" + ipaddress + "\t" + hostname + "\n"
    original.close()
    tmp = open(tmp_filename, 'wb')
    tmp.write(contents)
    tmp.close()

    os.system('sudo mv ' + tmp_filename + ' ' + filename)


def host_exists(hostname):
    """
    The exists function opens the host file and checks to see if the hostname requested exists in the host file.
    It opens the host file, reads the lines, and then a for loop checks each line to see if the hostname is in it.
    If it is, True is returned. If not, False is returned.
    """
    if 'linux' in sys.platform:
        filename = '/etc/hosts'
    f = open(filename, 'r')
    hostfiledata = f.readlines()
    f.close()
    for item in hostfiledata:
        if hostname in item:
            return True
    return False


def get_php_container():
    docker_compose = read_docker_compose()
    if docker_compose:
        return get_current_directory_name() + "_phpfpm_1"
    else:
        return False


def get_app_container():
    docker_compose = read_docker_compose()
    if docker_compose:
        return get_current_directory_name() + "_app_1"
    else:
        return False


def get_db_container():
    docker_compose = read_docker_compose()
    if docker_compose:
        return get_current_directory_name() + "_db_1"
    else:
        return False


def get_current_directory_name():
    path, current_directory = os.path.split(os.getcwd())
    return current_directory


def get_host_name():
    docker_compose = read_docker_compose()
    if docker_compose:
        return docker_compose['app']['environment']['VIRTUAL_HOST']
    else:
        return False


def get_db_root_password():
    docker_compose = read_docker_compose()
    if docker_compose:
        return docker_compose['db']['environment']['MYSQL_ROOT_PASSWORD']
    else:
        return False


def get_ip_address_of_container(container):
    cli = get_docker_client()
    metadata = cli.inspect_container(container)
    if isinstance(metadata, dict):
        if 'NetworkSettings' in metadata:
            if 'IPAddress' in metadata['NetworkSettings']:
                ipaddress = metadata['NetworkSettings']['IPAddress']
                if valid_ip(ipaddress):
                    return ipaddress
    return False