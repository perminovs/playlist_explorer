# Playlist organizer

![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

**playlist_organizer** is a command line tool to explore and compare your music library across Deezer and Spotify streaming services.

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
* register application on Deezer and Spotify and get tokens
* export env vars for auth as shown at .env_example

#### Run
```bash
python run.py
```
