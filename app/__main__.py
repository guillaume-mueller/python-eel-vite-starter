import backend
import eel
import eel.types
import psutil
import subprocess
import argparse
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
WEB_FILES_PATH = APP_DIR / 'frontend'
WEB_BUILD_PATH = WEB_FILES_PATH / 'build'
VITE_SERVER_HOST = 'localhost'
VITE_SERVER_PORT = 5173
EEL_SERVER_HOST = 'localhost'
EEL_SERVER_PORT = 8000

parser = argparse.ArgumentParser(
    formatter_class=argparse.RawTextHelpFormatter  # Keeps any '\n' in the help message
)
parser.add_argument(
    "--mode",
    choices=("install", "dev", "build", "run", "build-run"),
    default='build-run',
    help=
        "'install':   install the frontend dependencies\n"
        "'dev':       launch the frontend in development mode (Vite HMR)\n"
        "'build':     build the frontend in production mode\n"
        "'run':       launch the frontend in production mode using a prior build\n"
        "'build-run': build the frontend in production mode and launch it\n"
    )
args = parser.parse_args()

if args.mode == 'install':
    subprocess.call(
        "npm install".split(),
        cwd=WEB_FILES_PATH
    )

elif args.mode == 'dev':
    print("Starting npm process...")
    npm_process = subprocess.Popen(
        "npm run dev".split(),
        cwd=WEB_FILES_PATH
    )

    def on_eel_close(page: str, sockets: eel.types.WebSocketT):
        print("Closing npm process...")
        process = psutil.Process(npm_process.pid)
        for child in process.children(recursive=True):
            child.terminate()
        npm_process.terminate()
        npm_process.wait()
        exit()

    print("Starting Eel...")
    eel.init("dummy")
    eel.start(
        {
            "host": VITE_SERVER_HOST,
            "port": VITE_SERVER_PORT
        },
        host=EEL_SERVER_HOST,
        port=EEL_SERVER_PORT,
        close_callback=on_eel_close
    )

elif args.mode in ('build', 'run', 'build-run'):
    if args.mode in ('build', 'build-run'):
        print("Building the frontend...")
        if 0 != subprocess.call(
            "npm run build".split(),
            cwd=WEB_FILES_PATH
        ):
            print("An error occurred during the build, please check the logs")
            exit(1)
        if args.mode == 'build':
            exit()

    print("Starting Eel...")
    eel.init(WEB_BUILD_PATH)
    eel.start(
        'index.html',
        host=EEL_SERVER_HOST,
        port=EEL_SERVER_PORT
    )
