# Eel with Vite starter template, Svelte variant

A starter template for creating a GUI frontend with a JavaScript web framework via [Vite](https://vite.dev) for a Python backend via [Eel](https://pypi.org/project/Eel).

While this template uses [Svelte](https://svelte.dev), there's a similar one for Vue.js available in another branch.

## Key features

- Structured as a launchable Python package with some simple process managing to automate the interoperability between Eel and Node.js
- Development mode with Vite's Hot Module Replacement (HMR)
- Bidirectional communication in both development and production modes
- Focused on understanding how this works to keep full control instead of packaging a pretended solution

## Tested versions

- Linux Mint 22.1 (based on Ubuntu 24.04)
- Python 3.12.3
- Eel 0.18.1
- Chromium 135.0.7049.95
- Node.js 22.14.0
- Vite 6.3.1
- Svelte 5.23.1

## Setup

1. Install Python dependencies:
    ```sh
    pip install --requirement=requirements.txt
    ```

2. Create the Vite template with [Node.js package manager](https://nodejs.org/fr/download):
    ```sh
    cd app
    npm create vite@latest
    ```

    Choose :
    - Project name: `frontend`
    - Framework: `Svelte`
    - Variant: `JavaScript`

3. In `app/frontend/index.html`, add to `<head>`:
    ```html
    <script type="text/javascript" src="/eel.js"></script>
    ```

4. Update `app/frontend/vite.config.js`:
    ```js
    export default defineConfig(({ command }) => ({
        plugins: [svelte()],
        build: { outDir: "build" },
        ...(command === 'serve' && {  // dev mode config
            server: {
                host: 'localhost',
                port: 5173,
                proxy: {
                    '/eel': {
                        target: {
                            host: 'localhost',
                            port: 8000
                        },
                        ws: true  // WebSocket
                    }
                }
            }
        })
    }));
    ```

## Testing Communication

1. In `app/frontend/src/App.svelte`, add to `<script>`:
    ```js
    const eel = window.eel;
    let msg_to_python = $state("");

    function send_to_js(message) {
        console.log("Message received from Python: " + message);
    }
    window.eel.expose(send_to_js, 'send_to_js');  // ⚠️ must be called via `window.` and must get the name repeated as a string because the production build changes the functions names
    ```

2. Add to `<template>`:
    ```html
    <input type="text" bind:value={msg_to_python} placeholder="Message to Python" />
    <button onclick={() => eel.send_to_python(msg_to_python)}>Call Python</button>
    ```

### Production mode

1. Launch from project root:
    ```sh
    python -m app prod
    ```

2. Test:
   - [ ] Check the Python to JS message in DevTools (F12).
   - [ ] Send a message from JS to Python with the user interface and check the console output of Python.

### Development mode

1. Run from project root:
    ```sh
    python -m app dev
    ```

2. Test communication as in production mode.
3. Modify `<main>` content in `App.svelte` to test the HMR feature.

## Known Issues

1. **Memory leak**: Eel 0.18.1 has a [memory leak](https://github.com/python-eel/Eel/issues/757) for Python exposed function. Apply [this fix](https://github.com/python-eel/Eel/pull/760) if needed.

2. **Performance**: For sustained data streaming, the JSON constrain of Eel may be a bottleneck. Consider using [Flask-SocketIO](https://pypi.org/project/Flask-SocketIO) for binary format with a similar ease of use.
