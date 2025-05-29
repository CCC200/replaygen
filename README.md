# replaygen
Generate Pokemon Showdown replays from server logs automatically, and view them in-browser, old iOS style.

![Screenshot](https://i.imgur.com/ja8Jq7l.png)

## Install
Clone the repo and run `pip install -r requirements.txt`

## Usage
1. Copy `config-template.json` as `config.json`
2. Edit your config, pointing `log_dir` to the *logs* directory on your Showdown server, and `out_dir` to where you want the generated replays/index file to go
3. Run `py replaygen.py`

A full scan of all replays will be done at boot, and afterwards it will scan the most recent directory every 60 seconds.
