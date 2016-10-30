import click
from pathlib import Path
import requests
from clint.textui import progress
import tarfile
import os
import shutil
import glob
from jinja2 import Environment, PackageLoader
import subprocess
import sys
import docker
from docker.client import Client
from docker.utils import kwargs_from_env
import socket
import dockerpty
import yaml
from pprint import pprint


@click.group()
def main():
    pass


@click.option('--project-name', prompt=True, help='Project Name.')
@click.command()
def init(project_name):
    project_name = str(project_name)
    selected_release = get_release()
    with_sample_data = get_with_sample_data()
    prepare_project(project_name, selected_release, with_sample_data)
    add_docker_compose(project_name)

    # pprint (vars(response))


def get_with_sample_data():
    return click.confirm('with sample data?')


def subprocess_cmd(command, write_env=False, print_lines=True):
    process = subprocess.Popen(["sh"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    process.stdin.write(command + "\n")

    if write_env:
        process.stdin.write("env\n")

    process.stdin.close()

    response = ''

    for line in process.stdout:
        if print_lines:
            print line
        if write_env:
            name, value = line.strip().split("=", 1)
            os.environ[name] = value
        response += line

    return response


def add_docker_compose(project_name):
    env = Environment(loader=PackageLoader('magedock', 'templates'))
    template = env.get_template('docker-compose.yml')
    with open(project_name + "/" + "docker-compose.yml", "wb") as f:
        f.write(template.render(project_name=project_name))


def prepare_project(project_name, selected_release, with_sample_data):
    setup_directory(project_name)
    download_source(project_name, selected_release, with_sample_data)


def setup_directory(project_name):
    project_directory = Path(project_name)
    if project_directory.exists():
        click.echo('A directory with name "{0}" already exists'.format(project_name))
        sys.exit(0)
    else:
        project_directory.mkdir()


def download_source(project_name, selected_release, with_sample_data):
    file_name = selected_release['tag_name'] + ".tar.gz"
    download_url = "http://pubfiles.nexcess.net/magento/ce-packages/"

    if with_sample_data:
        file_name = "magento2-with-samples-" + file_name
    else:
        file_name = "magento2-" + file_name

    download_url += file_name

    if is_cached(file_name):
        file_path = is_cached(file_name)
        extract_file(file_path, project_name)
    else:
        file_path = project_name + "/" + file_name
        download_file(download_url, file_path)
        extract_file(file_path, project_name)
        cache_file(file_path, file_name)


def get_release():
    api_url = "https://api.github.com/repos/magento/magento2/releases"
    response = requests.get(api_url)
    if response.status_code != 200:
        click.echo('Not able to get list of Magento2 releases from {}'.format(api_url))
        sys.exit(0)
    else:
        releases = response.json()
        i = 0
        for release in releases:
            i += 1
            click.echo('[{}] {}'.format(i, release['tag_name']))
        selected_release_number = click.prompt('Magento version', type=click.IntRange(1, i), default=1)
        selected_release = releases[selected_release_number-1]
        return selected_release


def download_file(url, filename):
    click.echo('Downloading from '+url)
    r = requests.get(url, stream=True)

    # sometimes the response is empty, so try to re-request
    if r.headers.get('content-length') is None:
        return download_file(url, filename)

    with open(filename, 'wb') as f:
        total_length = int(r.headers.get('content-length'))
        for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
            if chunk:
                f.write(chunk)
    return filename


def extract_file(file_name, dest_path):
    click.echo('Extracting file ' + file_name)
    tar = tarfile.open(file_name)
    tar.extractall(dest_path)
    tar.close()


def cache_file(file_path, file_name):
    cache_dir = Path(os.path.expanduser('~') + "/.magedock")
    if not cache_dir.exists():
        cache_dir.mkdir()

    os.rename(file_path, str(cache_dir) + "/" + file_name)


def is_cached(file_name):
    cached_file = Path(os.path.expanduser('~') + "/.magedock/" + file_name)

    if cached_file.exists():
        return str(cached_file)
    else:
        return False


def move_files(src, dest):
    for filename in os.listdir(src):
        shutil.move(src + "/" + filename, dest + filename)
    os.rmdir(src)


@click.command()
@click.option('--container', help='Container Name (Optional)')
def ssh(container):
    if not container:
        docker_compose = read_docker_compose()
        if docker_compose:
            container = docker_compose['phpfpm']['hostname'] + "_1"
        else:
            sys.exit(0)

    kwargs = kwargs_from_env()
    kwargs['tls'].assert_hostname = False
    kwargs['version'] = '1.22'
    kwargs['timeout'] = 3

    cli = Client(**kwargs)

    # if not docker_ping(cli):
    #     if sys.platform == "darwin":
    #         dinghy_ip = subprocess_cmd(command="dinghy ip", print_lines=False)
    #         if not valid_ip(dinghy_ip):
    #             subprocess_cmd(command="dinghy start")
    #         subprocess_cmd(command="$(dinghy shellinit)", write_env=True, print_lines=False)

    if docker_ping(cli):
        try:
            dockerpty.exec_command(cli, container, "bash")
        except docker.errors.APIError as err:
            click.echo("Docker error: {0}".format(err))
            click.echo("Make sure you have run 'magedock start' first.")
    else:
        click.echo("Can't ping to docker\nMake sure you have run 'magedock start' first")


def valid_ip(address):
    try:
        socket.inet_aton(address)
        return True
    except:
        return False


def read_docker_compose():
    try:
        f = open('docker-compose.yml')
        dataMap = yaml.safe_load(f)
        f.close()
        return dataMap
    except:
        click.echo("File not found: docker-compose.yml\nmake sure you're in project directory.")
        return False


def docker_ping(cli):
    try:
        cli.ping()
        return True
    except:
        return False

main.add_command(init)
main.add_command(ssh)
