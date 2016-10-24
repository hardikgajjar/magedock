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
from pprint import pprint


@click.group()
def main():
    pass


@click.option('--project-name', prompt=True, help='Project Name.')
@click.command()
def init(project_name):
    project_name = str(project_name)
    selected_release = get_release()
    preapre_project(project_name, selected_release)
    add_docker_compose(project_name)
    start_docker_compose(project_name)

    # pprint (vars(response))

def start_docker_compose(project_name):
    subprocess_cmd("cd " + project_name + " && docker-compose up -d")

def subprocess_cmd(command):
    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
    proc_stdout = process.communicate()[0].strip()
    print proc_stdout

def add_docker_compose(project_name):
    env = Environment(loader=PackageLoader('magedock', 'templates'))
    template = env.get_template('docker-compose.yml')
    with open(project_name + "/" + "docker-compose.yml", "wb") as f:
        f.write(template.render(project_name=project_name))

def preapre_project(project_name, selected_release):
    setup_directory(project_name)
    download_source(project_name, selected_release)

def setup_directory(project_name):
    project_directory = Path(project_name)
    if project_directory.exists():
        click.echo('A directory with name "{0}" already exists'.format(project_name))
        return 0
    else:
        project_directory.mkdir()

def download_source(project_name, selected_release):
    file_name = project_name + "/" + "source.tar.gz"
    download_url = "http://pubfiles.nexcess.net/magento/ce-packages/magento2-" + selected_release['tag_name'] + ".tar.gz"
    download_file(download_url, file_name)
    extract_file(file_name, project_name)
    delete_file(file_name)
    # src = glob.glob(project_name + "/" + "magento*")
    # click.echo('Moving files to project directory')
    # move_files(src[0], project_name + "/")

def get_release():
    api_url = "https://api.github.com/repos/magento/magento2/releases"
    response = requests.get(api_url)
    if response.status_code != 200:
        click.echo('Not able to get list of Magento2 releases from {}'.format(api_url))
        return 0
    else:
        releases = response.json()
        i = 0
        for release in releases:
            i += 1
            click.echo('[{}] {}'.format(i, release['tag_name']))
        selected_release_number = click.prompt('Select a release number', type=click.IntRange(1, i), default=1)
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


def delete_file(file_name):
    os.remove(file_name)


def move_files(src, dest):
    for filename in os.listdir(src):
        shutil.move(src + "/" + filename, dest + filename)
    os.rmdir(src)

main.add_command(init)
