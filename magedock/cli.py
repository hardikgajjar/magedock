import click
from pathlib import Path
import requests

from pprint import pprint


# @click.argument('command', required=True)

@click.group()
def main():
    pass

@click.option('--project-name', prompt=True, help='Project Name.')
@click.command()
def init(project_name):
    project_directory = Path(str(project_name))

    if project_directory.exists():
        click.echo('A directory with name "{0}" already exists'.format(str(project_name)))
        return(0)
    else:
        project_directory.mkdir()

    api_url = "https://api.github.com/repos/magento/magento2/releases"
    response = requests.get(api_url)
    if response.status_code != 200:
        click.echo('Not able to get list of Magento2 releases from {}'.format(api_url))
        return(0)
    else:
        click.echo('Select a release number')
        i = 0
        for release in response.json():
            i += 1
            click.echo('[{}] {}'.format(i, release['tag_name']))
        selected_release = click.prompt('', type=click.IntRange(1, i), default=1)
        click.echo(selected_release)

    # pprint (vars(response))

main.add_command(init)
