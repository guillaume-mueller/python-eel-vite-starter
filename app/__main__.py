from . import launchers
import click
import rich.traceback

rich.traceback.install(suppress=[click])

@click.group(chain=True, invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    if ctx.invoked_subcommand is None:  # Default command
        ctx.invoke(prod)

@main.command(help="Install the frontend dependencies")
def install():
    launchers.install_frontend_dependencies()

@main.command(help="Launch the frontend in development mode (Vite HMR)")
def dev():
    launchers.launch_dev_mode()

@main.command(help="Build the frontend in production mode")
def build():
    launchers.build_frontend()

@main.command(help="Launch the frontend in production mode using a prior build")
def prod():
    launchers.launch_prod_mode()

if __name__ == '__main__':
    main()
