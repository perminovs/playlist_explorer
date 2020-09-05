# Playlist organizer

![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

### Why?
There are many tools to migrate your library from one music streaming platform to another, and they work fine.
If you want just to carefully migrate library, you should use one of such tool.

BUT.

While you collect your library on *source* platform, each playlist track has its own unique **adding time**, and it's possible to sort playlist by this column.
After migrating to *destination* platform **adding time** of each track will be equal, and such sorting will be no longer available.

Playlist organizer fixes it by comparing playlist content on both source and destination platforms and creating a playlist copy in destination with relative correct adding time.

By now it works (**to be honest it doesn't work, it's still WIP**) only with Deezer as source platform and Spotify as destination one.

### How to use
#### Preparing
* Register your own applications following [spotify guide](https://developer.spotify.com/documentation/general/guides/app-settings/) and [deezer app page](https://developers.deezer.com/myapps).
* Setup apps creds from previous step as environment variables or `.env` file (see `.env_example` for instance).
* Prepare running environment 
    ```bash
    virtualenv .venv --python=/usr/bin/python3
    source .venv/bin/activate
    pip install poetry
    poetry install
    ```

#### Run
```bash
python organizer/main.py
```
