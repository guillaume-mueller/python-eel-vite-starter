# A start template to use Eel with Vite

This procedure helps to start an environment with a web framework via Vite communicating to a Python backend with Eel.

It allows both the use of Vite's Hot Module Replacement (HMR) feature for development and to build the project for production, with bidirectional communication working in both modes.

It will use Vue.js but has also been tested with Svelte, which only needs the obvious adjustments to work.

Tested versions:
- Linux Mint 22.1 (based on Ubuntu 24.04)
- Python 3.12.3
- Eel 0.18.1
- Node.js 22.14.0
- Vite 6.3.1
- Vue.js 3.5.13
- Svelte 5.23.1

## Installation

Install Eel:

```sh
pip install eel
```

Create the Vite template:

```sh
cd app
npm create vite@latest
```

Choose :
- project name: `frontend`,
- framework: `Vue`,
- variant: `JavaScript`.

Install the node modules:

```sh
cd frontend
npm install
```

In `app/frontend/index.html`, add the following line within the `<head>` tag:

```html
<script type="text/javascript" src="/eel.js"></script>
```

In `app/frontend/vite.config.js`, replace the `export default defineConfig […]` call by the following:

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

## Basic usage and test

In `app/frontend/src/components/HelloWorld.vue`, add the following line within the `<script setup>` tag:

```js
const eel = window.eel;

const msg_to_python = ref('');

function send_to_js(message) {
    console.log("Message received from Python: " + message);
}
window.eel.expose(send_to_js, 'send_to_js');  // ⚠️ must be called via `window.` and must get the name repeated as a string because the production build changes the functions name
```

Still in `app/frontend/src/components/HelloWorld.vue`, add the following line within the `<template>` tag:

```html
<input type="text" placeholder="Message to Python" v-model="msg_to_python"/>
<button @click="eel.send_to_python(msg_to_python)">Send to Python</button>
```

### Production mode

Try to run the app in production mode with the following command (from the root directory of the project):

```sh
python app
```

Test to send a message from JS to Python and check in DevTools (F12) that the message from Python to JS is received.

### Development mode

Try to run the app in development mode with the following command:

```sh
python app --mode=dev
```

Test the same bidirectional communication as in production mode.

In the file `app/frontend/src/components/HelloWorld.vue`, modify something within the `<template>` tag and check that the changes are applied in the Eel window without having to restart the program.

## Notes

As of Eel 0.18.1, [there's a memory leak](https://github.com/python-eel/Eel/issues/757) making that every data communicated from Python to JS remains in memory. To avoid it, one can apply [this fix](https://github.com/python-eel/Eel/pull/760).

Regarding performances for streaming, if the data is not adapted to JSON, one can use Flask-SocketIO (or maybe only SocketIO) very easily to stream data via WebSocket in binary format with the same kind of syntax as Eel.
