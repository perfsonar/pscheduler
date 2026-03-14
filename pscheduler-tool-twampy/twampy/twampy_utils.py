###
# Utilities used by twampy tool plugin
#

from twampy_defaults import *
import configparser
import pscheduler
import shutil

# Role constants
CLIENT_ROLE = 0
SERVER_ROLE = 1

log = pscheduler.Log(prefix="tool-twampy", quiet=True)


def get_role(participant, test_spec):
    """Determine whether participant will act as client or server.
    STAMP is single-participant (sender only), so always return CLIENT_ROLE.
    """
    return CLIENT_ROLE


def get_config():
    """Read configuration file."""
    config = None
    try:
        config = configparser.ConfigParser()
        config.read(CONFIG_FILE)
    except Exception:
        log.warning("Unable to read configuration file %s. Proceeding with defaults." % CONFIG_FILE)
    return config


def find_twampy():
    """Find the twampy command. Returns path or None."""
    config = get_config()

    # Check config file first
    if config and config.has_option(CONFIG_SECTION, CONFIG_OPT_TWAMPY_CMD):
        cmd = config.get(CONFIG_SECTION, CONFIG_OPT_TWAMPY_CMD)
        if shutil.which(cmd):
            return cmd

    # Try default locations
    for candidate in ['twampy', '/usr/local/bin/twampy', '/usr/bin/twampy']:
        path = shutil.which(candidate)
        if path:
            return path

    return None
