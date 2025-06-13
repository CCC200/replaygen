# replaygen
Generate Pokemon Showdown replays from server logs automatically, and view them in-browser, old iOS style.

![Screenshot](https://i.imgur.com/iZOsISS.png)

## Install
Clone the repo and run `pip install -r requirements.txt`

## Usage
1. Copy `config-template.json` as `config.json`
2. Edit your config, pointing `log_dir` to the *logs* directory on your Showdown server, and `out_dir` to where you want the generated replays/index file to go
3. Run `py replaygen.py`

A full scan of all replays will be done at boot, and afterwards it will scan the most recent directory every 60 seconds.

## Optional params
There are some additional parameters you can add to your config file:
- **client_url**: String pointing to a specific Showdown client. Useful if your server has formats with custom sprites, backgrounds etc.
- **formats**: An array of format names, i.e. `"formats": ["gen1ou", "gen2ou"]` etc. Will only generate replays for matching games.
