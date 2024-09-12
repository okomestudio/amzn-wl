"""App config.

Allow an INI file to change some configuration items."""

import configparser
import pathlib

ini_path = pathlib.Path(".amzn-wl.ini")

config = configparser.ConfigParser()

# Set default values
config["driver"] = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36",
    "languages": "en-US en",
    "vendor": "Google inc.",
    "platform": "Win32",
    "webgl_vendor": "Intel Inc.",
    "renderer": "Intel Iris OpenGL Engine",
    "fix_hairline": "True",
}

if ini_path.exists():
    config.read(str(ini_path))
