import backend
import eel, eel.types
import psutil, subprocess
import argparse
from pathlib import Path

THIS_FILE_PATH = Path(__file__).resolve().parent
WEB_FILES_PATH = THIS_FILE_PATH / 'frontend'
WEB_INSTALLS_PATH = WEB_FILES_PATH / 'node_modules'
WEB_BUILD_PATH = WEB_FILES_PATH / 'build'
WEB_DEV_PATH = WEB_FILES_PATH / 'src'
WEB_FILES_EXTENSIONS = ('.svelte', '.js')  # To search Eel-exposed functions

VITE_DEV_SERVER_HOST = 'localhost'
VITE_DEV_SERVER_PORT = 5173
EEL_SERVER_HOST = 'localhost'
EEL_SERVER_PORT = 8000

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter  # Keeps any '\n' in the help message
)
parser.add_argument(
    "mode",
    metavar='mode=build-launch',
    choices=("install", "dev", "build-launch", "build", "launch"),
    nargs='?',  # Optional argument
    default='build-launch',
    help=
        "'install':      install the frontend dependencies\n"
        "'dev':          launch the frontend in development mode (Vite HMR)\n"
        "'build-launch': build the frontend in production mode and launch it\n"
        "'build':        build the frontend in production mode\n"
        "'launch':       launch the frontend in production mode using a prior build\n"
    )
args = parser.parse_args()

if args.mode == 'install' or not WEB_INSTALLS_PATH.exists():
    if 0 != subprocess.call(
        "npm install".split(),
        cwd=WEB_FILES_PATH
    ):
        exit(1)
    if args.mode == 'install':
        exit()

if args.mode == 'dev':
    npm_process = subprocess.Popen(
        "npm run dev".split(),
        cwd=WEB_FILES_PATH
    )
    init_path = WEB_DEV_PATH
    start_urls = {
        'host': VITE_DEV_SERVER_HOST,
        'port': VITE_DEV_SERVER_PORT
    }
    def close_callback(page: str, sockets: eel.types.WebSocketT):
        process = psutil.Process(npm_process.pid)
        children = process.children(recursive=True)
        for child in children:
            child.terminate()
        psutil.wait_procs(children)
        npm_process.terminate()
        npm_process.wait()
        exit()

if 'build' in args.mode:
    if 0 != subprocess.call(
        "npm run build".split(),
        cwd=WEB_FILES_PATH
    ):
        exit(1)
    if args.mode == 'build':
        exit()

if 'launch' in args.mode:
    init_path = WEB_BUILD_PATH
    start_urls = 'index.html'
    close_callback = None

eel.init(init_path, allowed_extensions=WEB_FILES_EXTENSIONS)
eel.send_to_js("Hello from Python !")
eel.start(
    start_urls,
    host=EEL_SERVER_HOST,
    port=EEL_SERVER_PORT,
    close_callback=close_callback
)
