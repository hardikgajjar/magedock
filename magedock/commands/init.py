import click
from pathlib import Path
import requests
from clint.textui import progress
import tarfile
import os
import shutil
from jinja2 import Environment, PackageLoader
import sys
import helper as helper
from click_help_colors import HelpColorsCommand


@click.command(
    cls=HelpColorsCommand,
    help_headers_color='yellow',
    help_options_color='green'
)
@click.option('--project-name', prompt=True, help='Project Name')
def init(project_name):
    """Create new Project"""
    project_name = str(project_name)
    selected_release = get_release()
    with_sample_data = get_with_sample_data()
    prepare_project(project_name, selected_release, with_sample_data)
    add_docker_compose(project_name)
    npm_install(project_name)


def get_release():
    api_url = "https://api.github.com/repos/magento/magento2/releases"
    response = requests.get(api_url)
    if response.status_code != 200:
        helper.error_message('Not able to get list of Magento2 releases from {}'.format(api_url))
        sys.exit(0)
    else:
        releases = response.json()
        i = 0
        for release in releases:
            i += 1
            helper.warning_message('[{}] {}'.format(i, release['tag_name']))
        selected_release_number = click.prompt('Magento version', type=click.IntRange(1, i), default=1)
        selected_release = releases[selected_release_number-1]
        return selected_release


def get_with_sample_data():
    return click.confirm('with sample data?')


def prepare_project(project_name, selected_release, with_sample_data):
    setup_directory(project_name)
    download_source(project_name, selected_release, with_sample_data)


def add_docker_compose(project_name):
    env = Environment(loader=PackageLoader('magedock', 'templates'))
    template = env.get_template('docker-compose.yml')
    with open(project_name + "/" + "docker-compose.yml", "wb") as f:
        f.write(template.render(project_name=project_name))


def setup_directory(project_name):
    project_directory = Path(project_name)
    if project_directory.exists():
        helper.error_message('A directory with name "{0}" already exists'.format(project_name))
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


def download_file(url, filename):
    helper.warning_message('Downloading from '+url)
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
    helper.warning_message('Extracting file ' + file_name)
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


def npm_install(project_name):
    helper.warning_message('Installing node modules')
    src = project_name + "/package.json.sample"
    dest = project_name + "/package.json"
    os.rename(src, dest)
    src = project_name + "/Gruntfile.js.sample"
    dest = project_name + "/Gruntfile.js"
    os.rename(src, dest)
    helper.subprocess_cmd(command='cd '+project_name+' && npm install')
