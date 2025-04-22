"""
This module is responsible for launching Eel and Vite.

Functions depending on others check for the presence of the folders the latters create to eventually call them.

Most constants are defined to match Node.js and Vite defaults and options set in `vite.config.js`.
"""

from . import backend  # Eel-exposed functions
from . import utils
import eel, eel.types
import subprocess
from pathlib import Path
import sys
from typing import Iterable, Dict, Callable, Any

THIS_FILE_FOLDER_PATH = Path(__file__).resolve().parent
WEB_FILES_PATH = THIS_FILE_FOLDER_PATH / 'frontend'
WEB_INSTALLS_PATH = WEB_FILES_PATH / 'node_modules'
WEB_PROD_BUILD_PATH = WEB_FILES_PATH / 'build'
WEB_PROD_INDEX_FILE_NAME = 'index.html'
WEB_DEV_SRC_PATH = WEB_FILES_PATH / 'src'
WEB_DEV_FILES_EXTENSIONS = ('.svelte', '.js')  # To search Eel-exposed functions in dev mode
WEB_DEV_LAUNCH_TIMEOUT = 30  # [s], timeout for the Vite dev server to start

VITE_DEV_SERVER_HOST = 'localhost'
VITE_DEV_SERVER_PORT = 5173
EEL_SERVER_HOST = 'localhost'
EEL_SERVER_PORT = 8000

def install_frontend_dependencies():
    print("Installing frontend dependencies...")
    if 0 != subprocess.call("npm install".split(), cwd=WEB_FILES_PATH):
        raise RuntimeError("`npm install` failed")

def build_frontend():
    if not WEB_INSTALLS_PATH.exists():
        install_frontend_dependencies()
    print("Building frontend...")
    if 0 != subprocess.call("npm run build".split(), cwd=WEB_FILES_PATH):
        raise RuntimeError("`npm run build` failed")

def launch_prod_mode():
    if not WEB_PROD_BUILD_PATH.exists():
        build_frontend()
    print("Launching frontend in production mode...")
    _start_eel(
        init_path=WEB_PROD_BUILD_PATH,
        start_urls=WEB_PROD_INDEX_FILE_NAME
    )

def launch_dev_mode():
    if not WEB_INSTALLS_PATH.exists():
        install_frontend_dependencies()
    print("Launching frontend in development mode...")
    npm_process = subprocess.Popen("npm run dev".split(), cwd=WEB_FILES_PATH)  # Async

    print("Waiting for Vite dev server to start...")
    if not utils.block_until_server_is_alive(
        f"http://{VITE_DEV_SERVER_HOST}:{VITE_DEV_SERVER_PORT}",
        timeout=WEB_DEV_LAUNCH_TIMEOUT
    ):
        utils.terminate_process_and_children(npm_process.pid)
        raise RuntimeError(
            f"Vite dev server failed to start within {WEB_DEV_LAUNCH_TIMEOUT} seconds"
        )

    _start_eel(
        init_path=WEB_DEV_SRC_PATH,
        start_urls={"host": VITE_DEV_SERVER_HOST, "port": VITE_DEV_SERVER_PORT},
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
    eel.init(init_path, allowed_extensions=WEB_DEV_FILES_EXTENSIONS)
    eel.send_to_js("Hello from Python !")
    eel.start(
        start_urls,
        host=EEL_SERVER_HOST,
        port=EEL_SERVER_PORT,
        close_callback=close_callback
    )
