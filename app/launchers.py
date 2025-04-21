from . import backend  # Needed for Eel-exposed functions
import eel, eel.types
import psutil, subprocess
from pathlib import Path
import sys
from typing import Iterable, Dict, Callable, Any

THIS_FILE_FOLDER_PATH = Path(__file__).resolve().parent
WEB_FILES_PATH = THIS_FILE_FOLDER_PATH / 'frontend'
WEB_INSTALLS_PATH = WEB_FILES_PATH / 'node_modules'
WEB_PROD_PATH = WEB_FILES_PATH / 'build'
WEB_PROD_INDEX_FILE_NAME = 'index.html'
WEB_DEV_PATH = WEB_FILES_PATH / 'src'
WEB_DEV_FILES_EXTENSIONS = ('.vue', '.js')  # To search Eel-exposed functions

VITE_DEV_SERVER_HOST = 'localhost'
VITE_DEV_SERVER_PORT = 5173
EEL_SERVER_HOST = 'localhost'
EEL_SERVER_PORT = 8000

def install_frontend_dependencies():
    print("Installing frontend dependencies...")
    if 0 != subprocess.call("npm install".split(), cwd=WEB_FILES_PATH):
        raise RuntimeError("`npm install` failed")

def launch_dev_mode():
    if not WEB_INSTALLS_PATH.exists():
        install_frontend_dependencies()
    print("Launching frontend in development mode...")
    npm_process = subprocess.Popen(  # Asynchronous
        "npm run dev".split(),
        cwd=WEB_FILES_PATH
    )
    if npm_process.poll() is not None:
        raise RuntimeError("`npm run dev` stopped unexpectedly")

    def close_callback(page: str, sockets: eel.types.WebSocketT):
        process = psutil.Process(npm_process.pid)
        children = process.children(recursive=True)
        for child in children : child.terminate()
        psutil.wait_procs(children)
        npm_process.terminate()
        npm_process.wait()
        sys.exit(0)

    _start_eel(
        init_path=WEB_DEV_PATH,
        start_urls={
            'host': VITE_DEV_SERVER_HOST,
            'port': VITE_DEV_SERVER_PORT
        },
        close_callback=close_callback
    )

def build_frontend():
    if not WEB_INSTALLS_PATH.exists():
        install_frontend_dependencies()
    print("Building frontend...")
    if 0 != subprocess.call("npm run build".split(), cwd=WEB_FILES_PATH):
        raise RuntimeError("`npm run build` failed")

def launch_prod_mode():
    if not WEB_INSTALLS_PATH.exists():
        build_frontend()
    print("Launching frontend in production mode...")
    _start_eel(init_path=WEB_PROD_PATH, start_urls=WEB_PROD_INDEX_FILE_NAME)

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
