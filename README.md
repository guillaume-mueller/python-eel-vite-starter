# Installation of an environment to use Vue.js via Vite with Eel

This procedure explains how to install an environment to use Vue.js via Vite with Eel. It allows both the use of Vite's Hot Module Replacement (HMR) feature for development and to build the project for production. It has only been tested to call a Python function from a Vue component and not the opposite.

It has been tested on Linux Mint 22.1 (based on Ubuntu 24.04) with Python 3.12.3.

## Installation

Install Eel (tested version: 0.18.1):

```sh
pip install eel
```

Create the Vite template (tested version: 6.3.1):

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
  ...(command === 'serve' && {
    server: {
      proxy: {
        '/eel': {
          target: 'http://localhost:8000',  // "host" and "port_eel" in __main__.py
          ws: true
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
python app --mode=prod
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
