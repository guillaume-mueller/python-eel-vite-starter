import eel_api
import eel
import psutil
import subprocess
import argparse

WEB_FILES_PATH = 'vite-project'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=("dev", "prod"),
        default="prod",
        help="Launch the app in development (Vite HMR) or production mode"
    )
    args = parser.parse_args()

    if args.mode == 'dev':
        npm_process = subprocess.Popen(
            "npm run dev".split(),
            cwd=WEB_FILES_PATH
        )

        eel.init("dummy")

        def on_eel_close(page, sockets):
            print("Closing npm process...")
            process = psutil.Process(npm_process.pid)
            for child in process.children(recursive=True):
                child.terminate()
            npm_process.terminate()
            npm_process.wait()
            exit()

        eel.start(
            {"port": 5173, "host": "localhost", "port_eel": 8000},
            close_callback=on_eel_close,
        )

    elif args.mode == 'prod':
        if 0 != subprocess.call("npm run build".split(), cwd=WEB_FILES_PATH):
            print("An error occurred during the build, please check the logs")
            exit(1)
        eel.init(f"{WEB_FILES_PATH}/dist")
        eel.start('index.html')
