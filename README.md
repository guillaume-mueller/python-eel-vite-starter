# Installation of an environment to use Eel with Vite

This procedure explains how to install an environment with a web framework via Vite communicating to a Python backend with Eel.

It allows both the use of Vite's Hot Module Replacement (HMR) feature for development and to build the project for production.

It isn't able to call a JavaScript function from Python yet.

It will use Vue.js but has also been tested with Svelte, which only needs minor obvious adjustments to work.

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

In `app/frontend/vite.config.js`, replace the `export default defineConfig […]` call by the following (`command === 'serve'` makes it only applied for the development mode):

```js
export default defineConfig(({ command }) => ({
    plugins: [vue()],
    build: {
        outDir: "build",
    },
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
}))
```

## Basic usage and test

In `app/frontend/src/components/HelloWorld.vue`, add the following line within the `<script setup>` tag:

```js
const eel = window.eel;
```

Still in `app/frontend/src/components/HelloWorld.vue`, add the following line within the `<template>` tag:

```html
<button @click="eel.hello()">Call Python</button>
```

### Production mode

Try to run the app in production mode with the following command (from the root directory of the project):

```sh
python app --mode=build-run
```

Click on the button `Call Python` and check that the terminal displays `Hello !`.

### Development mode

Try to run the app in development mode with the following command:

```sh
python app --mode=dev
```

Click on the button `Call Python` and check that the terminal displays `Hello !`.

In the file `app/frontend/src/components/HelloWorld.vue`, modify something within the `<template>` tag and check that the changes are applied in the Eel window without having to restart the program.

## TODO

- [ ] Call a JavaScript function from Python.
