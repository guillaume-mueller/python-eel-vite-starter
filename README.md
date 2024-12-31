# Installation of an environnement to use Vue.js via Vite with eel

This procedure explains how to install an environnement to use Vue.js via Vite with eel. It allows both to use the hot reload feature of Vite and to build the project for production. It has only been tested to call a Python function from a Vue component and not the opposite.

It has been tested on Linux Mint 22 (based on Ubuntu 24.04).

## Installation

Install eel (tested version: 0.18.1):

```sh
pip install eel
```

Create the vite template (tested version: 6.1.1):

```sh
npm create vite@latest
```

Let the default project name: `vite-project`.

Select `Vue` as the framework.

Select `JavaScript` as the variant.

Install the node modules:

```sh
cd vite-project
npm install
```

In `vite-project/index.html`, add the following line within the `<head>` tag:

```html
<script type="text/javascript" src="/eel.js"></script>
```

In `vite-project/vite.config.js`, replace the `export default defineConfig […]` call by the following (`command === 'serve'` makes it only applied for the development mode):

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

In `vite-project/src/components/HelloWorld.vue`, add the following line within the `<script setup>` tag:

```js
const eel = window.eel
```

Still in `vite-project/src/components/HelloWorld.vue`, add the following line within the `<template>` tag:

```html
<button @click="eel.hello()">Call Python</button>
```

### Production mode

Try to run the program in production mode with the following command:

```sh
python __main__.py
```

Click on the button `Call Python` and check that the terminal displays `Hello !`.

### Development mode

Try to run the program in development mode with the following command (it can takes up to about 10 seconds to open the eel window):

```sh
python __main__.py --mode=dev
```

Click on the button `Call Python` and check that the terminal displays `Hello !`.

In the file `vite-project/src/components/HelloWorld.vue`, modify something within the `<template>` tag and check that the changes are applied in the eel window without having to restart the program.

## TODO

- [ ] Call a JavaScript function from Python.
- [ ] Speed up the opening of the eel window in development mode.
