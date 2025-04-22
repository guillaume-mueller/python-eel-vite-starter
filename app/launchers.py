"""
This module is responsible for launching Eel and Vite.

Functions depending on others check for the presence of the folders the latters create to eventually call them.
"""

from . import backend  # Eel-exposed functions
from . import utils
import eel, eel.types
import dotenv
import subprocess
from pathlib import Path
import sys
from typing import Iterable, Dict, Callable, Any

THIS_FILE_FOLDER_PATH = Path(__file__).resolve().parent

ENV = dotenv.dotenv_values(THIS_FILE_FOLDER_PATH / '.env')

FRONTEND_PATH = THIS_FILE_FOLDER_PATH / 'frontend'
NODE_MODULES_PATH = FRONTEND_PATH / 'node_modules'
BUILD_PATH = FRONTEND_PATH / ENV['BUILD_DIR']
DEV_SRC_PATH = FRONTEND_PATH / 'src'
DEV_FILES_EXTENSIONS = ('.vue', '.js')  # To search Eel-exposed functions in dev mode
DEV_LAUNCH_TIMEOUT = 10  # [s], timeout for the Vite dev server to start
NPM = 'npm'  # or 'yarn', 'pnpm', etc.

class NpmError(Exception):
    pass

def install_frontend_dependencies():
    """
    Raises:
        NpmError: if the command fails
    """
    print("Installing frontend dependencies...")
    if 0 != subprocess.call(f"{NPM} install".split(), cwd=FRONTEND_PATH):
        raise NpmError(f"`{NPM} install` failed")

def build_frontend():
    """
    Raises:
        NpmError: if the command fails
    """
    if not NODE_MODULES_PATH.exists():
        install_frontend_dependencies()
    print("Building frontend...")
    if 0 != subprocess.call(f"{NPM} run build".split(), cwd=FRONTEND_PATH):
        raise NpmError(f"`{NPM} run build` failed")

def launch_prod_mode():
    if not BUILD_PATH.exists():
        build_frontend()
    print("Launching frontend in production mode...")
    _start_eel(
        init_path=BUILD_PATH,
        start_urls='index.html'
    )

def launch_dev_mode():
    """
    Raises:
        Exception: if the Vite dev server failed to start within the timeout
    """
    if not NODE_MODULES_PATH.exists():
        install_frontend_dependencies()
    print("Launching frontend in development mode...")
    npm_process = subprocess.Popen(  # Async
        f"{NPM} run dev".split(),
        cwd=FRONTEND_PATH
    )

    print("Waiting for Vite dev server to start...")
    if not utils.block_until_server_is_alive(
        f"http://{ENV['DEV_HOST']}:{ENV['DEV_PORT']}",
        timeout=DEV_LAUNCH_TIMEOUT
    ):
        utils.terminate_process_and_children(npm_process.pid)
        raise Exception(
            f"Vite dev server failed to start within {DEV_LAUNCH_TIMEOUT} seconds"
        )

    _start_eel(
        init_path=DEV_SRC_PATH,
        start_urls={"host": ENV['DEV_HOST'], "port": ENV['DEV_PORT']},
        close_callback=lambda page, sockets: (
            utils.terminate_process_and_children(npm_process.pid),
            sys.exit(0),
        )
    )

def _start_eel(
    init_path: str | Path,
    start_urls: Iterable[str | Dict[str, str]],
    close_callback: Callable[[str, eel.types.WebSocketT], Any] | None = None
):
    eel.init(init_path, allowed_extensions=DEV_FILES_EXTENSIONS)
    eel.send_to_js("Hello from Python !")
    eel.start(
        start_urls,
        host=ENV['EEL_HOST'],
        port=ENV['EEL_PORT'],
        close_callback=close_callback
    )
