# Eel with Vite starter template

A starter template for creating web applications using Vite with Python Eel backend integration.

Key features:
- Development mode with Vite's Hot Module Replacement (HMR)
- Bidirectional communication in both development and production modes

While this template uses Vue.js, there's a similar one for Svelte available in another branch.

Tested versions:
- Linux Mint 22.1 (based on Ubuntu 24.04)
- Python 3.12.3
- Eel 0.18.1
- Node.js 22.14.0
- Vite 6.3.1
- Vue.js 3.5.13

## Setup

1. Install Eel:
    ```sh
    pip install eel
    ```

2. Create the Vite template:
    ```sh
    cd app
    npm create vite@latest
    ```

    Choose :
    - Project name: `frontend`
    - Framework: `Vue`
    - Variant: `JavaScript`

3. In `app/frontend/index.html`, add to `<head>`:
    ```html
    <script type="text/javascript" src="/eel.js"></script>
    ```

4. Update `app/frontend/vite.config.js`:
    ```js
    export default defineConfig(({ command }) => ({
        plugins: [vue()],
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

1. In `app/frontend/src/components/HelloWorld.vue`, add to `<script setup>`:
    ```js
    const eel = window.eel;
    const msg_to_python = ref('');

    function send_to_js(message) {
        console.log("Message received from Python: " + message);
    }
    window.eel.expose(send_to_js, 'send_to_js');  // ⚠️ must be called via `window.` and must get the name repeated as a string because the production build changes the functions names
    ```

2. Add to `<template>`:
    ```html
    <input type="text" placeholder="Message to Python" v-model="msg_to_python"/>
    <button @click="eel.send_to_python(msg_to_python)">Send to Python</button>
    ```

### Production mode

1. Run from project root:
    ```sh
    python app build-run
    ```

2. Test:
   - [ ] Check the Python to JS message in DevTools (F12).
   - [ ] Send a message from JS to Python with the user interface and check the console output of Python.

### Development mode

1. Start dev server:
    ```sh
    python app dev
    ```

2. Test communication as in production mode.
3. Modify the `<template>` in `HelloWorld.vue` to test the HMR feature.

## Known Issues

1. **Memory leak**: Eel 0.18.1 has a [memory leak](https://github.com/python-eel/Eel/issues/757) for Python exposed function. Apply [this fix](https://github.com/python-eel/Eel/pull/760) if needed.

2. **Performance**: For sustained streaming, the JSON constrain of Eel may be a bottleneck. Consider using Flask-SocketIO for binary format with a similar ease of use.
