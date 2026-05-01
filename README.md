# e6postgetter
This is a Python3 Flask app to fetch and return random posts from e621/e926 similar to yiff.gay

## How to use?
- create a user and apikey on e621
- create python3 virtual environment with `python3 -m venv /path/to/venv`
- install required python dependencies with `pip3 install -r requirements.txt`
- optionally install and customize the provided systemd service (`systemd/e6postgetter.service`) to `/lib/systemd/system/e6postgetter.service` 
- fill out your credentials and other info in `env.sample` and save it as `.env`
