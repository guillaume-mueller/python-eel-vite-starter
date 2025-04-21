import backend
import eel, eel.types
import psutil, subprocess
import click
from pathlib import Path
import sys

THIS_FILE_PATH = Path(__file__).resolve().parent
WEB_FILES_PATH = THIS_FILE_PATH / 'frontend'
WEB_INSTALLS_PATH = WEB_FILES_PATH / 'node_modules'
WEB_PROD_PATH = WEB_FILES_PATH / 'build'
WEB_DEV_PATH = WEB_FILES_PATH / 'src'
WEB_FILES_EXTENSIONS = ('.vue', '.js')  # To search Eel-exposed functions

VITE_DEV_SERVER_HOST = 'localhost'
VITE_DEV_SERVER_PORT = 5173
EEL_SERVER_HOST = 'localhost'
EEL_SERVER_PORT = 8000

def start_eel(init_path, start_urls, close_callback=None):
    eel.init(init_path, allowed_extensions=WEB_FILES_EXTENSIONS)
    eel.send_to_js("Hello from Python !")
    eel.start(
        start_urls,
        host=EEL_SERVER_HOST,
        port=EEL_SERVER_PORT,
        close_callback=close_callback
    )

@click.group(chain=True, invoke_without_command=True)
@click.pass_context
def main(ctx: click.Context):
    if ctx.invoked_subcommand is None:  # Default
        ctx.invoke(prod)

@main.command(help="Install the frontend dependencies")
def install():
    click.echo("Installing frontend dependencies...")
    if 0 != subprocess.call("npm install".split(), cwd=WEB_FILES_PATH):
        click.echo("Error: `npm install` failed", err=True)
        sys.exit(1)

@main.command(help="Launch the frontend in development mode (Vite HMR)")
@click.pass_context
def dev(ctx: click.Context):
    if not WEB_INSTALLS_PATH.exists():
        ctx.invoke(install)
    click.echo("Launching frontend in development mode...")
    npm_process = subprocess.Popen(  # Asynchronous
        "npm run dev".split(),
        cwd=WEB_FILES_PATH
    )
    if 0 == npm_process.poll():
        click.echo("Error: `npm run dev` failed", err=True)
        sys.exit(1)

    def close_callback(page: str, sockets: eel.types.WebSocketT):
        process = psutil.Process(npm_process.pid)
        children = process.children(recursive=True)
        for child in children : child.terminate()
        psutil.wait_procs(children)
        npm_process.terminate()
        npm_process.wait()
        sys.exit(0)

    start_eel(
        init_path=WEB_DEV_PATH,
        start_urls={
            'host': VITE_DEV_SERVER_HOST,
            'port': VITE_DEV_SERVER_PORT
        },
        close_callback=close_callback
    )

@main.command(help="Build the frontend in production mode")
@click.pass_context
def build(ctx: click.Context):
    if not WEB_INSTALLS_PATH.exists():
        ctx.invoke(install)
    click.echo("Building frontend in production mode...")
    if 0 != subprocess.call("npm run build".split(), cwd=WEB_FILES_PATH):
        click.echo("Error: `npm run build` failed", err=True)
        sys.exit(1)

@main.command(help="Launch the frontend in production mode using a prior build")
@click.pass_context
def prod(ctx: click.Context):
    if not WEB_INSTALLS_PATH.exists():
        ctx.invoke(build)
    start_eel(
        init_path=WEB_PROD_PATH,
        start_urls='index.html'
    )

if __name__ == '__main__':
    main()
