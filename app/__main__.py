"""The CLI entry point for the application."""

from . import launchers
import rich.traceback
import click

rich.traceback.install(suppress=[click])

@click.group(
    chain=True,
    invoke_without_command=True,
    context_settings={'max_content_width': 120},
    help=
        "Launch Eel and Vite.\n\n"
        "The commands can be chained.\n\n"
        "On a first run, commands depending on others may call them automatically priorly."
)
@click.pass_context
def main(ctx: click.Context):
    if ctx.invoked_subcommand is None:  # If no command is given (default)
        ctx.invoke(prod)

@main.command()
def install():
    """Install the frontend dependencies"""
    launchers.install_frontend_dependencies()

@main.command()
def dev():
    """Launch Eel and the frontend in development mode (Vite HMR) and connect them"""
    launchers.launch_dev_mode()

@main.command()
def build():
    """Build the frontend for production mode"""
    launchers.build_frontend()

@main.command()
def prod():
    """(DEFAULT) Launch the frontend with Eel in production mode using a prior build"""
    launchers.launch_prod_mode()

if __name__ == '__main__':
    main()
