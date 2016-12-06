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
def db():
    """Show database connection information"""
    db_container_ipaddress = helper.get_ip_address_of_container(helper.get_db_container())

    click.secho("MySQL", fg='green', bold=True, underline=True)
    helper.warning_message("Host: ", nl=False)
    helper.success_message(db_container_ipaddress)
    helper.warning_message("Username: ", nl=False)
    helper.success_message("root")
    helper.warning_message("Password: ", nl=False)
    helper.success_message(helper.get_db_root_password())

    if sys.platform == "darwin":
        click.echo("")
        click.secho("SSH Tunnel", fg='green', bold=True, underline=True)
        helper.warning_message("Host: ", nl=False)
        helper.success_message(helper.get_host_name())
        helper.warning_message("Username: ", nl=False)
        helper.success_message("docker")
        helper.warning_message("Password: ", nl=False)
        helper.success_message("tcuser")
        click.echo("")
        click.secho("You have to connect MySQL via SSH Tunnel", fg='blue')
