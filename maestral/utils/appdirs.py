# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 31 16:23:13 2018

@author: samschott
"""
import platform
import os
import os.path as osp
import logging

logger = logging.getLogger(__name__)


def get_home_dir():
    """
    Returns user home directory. This will be determined from the first
    valid result out of (osp.expanduser("~"), $HOME, $USERPROFILE, $TMP).
    """
    try:
        # expanduser() returns a raw byte string which needs to be
        # decoded with the codec that the OS is using to represent
        # file paths.
        path = osp.expanduser("~")
    except Exception:
        path = ''

    if osp.isdir(path):
        return path
    else:
        # Get home from alternative locations
        for env_var in ("HOME", "USERPROFILE", "TMP"):
            # os.environ.get() returns a raw byte string which needs to be
            # decoded with the codec that the OS is using to represent
            # environment variables.
            path = os.environ.get(env_var, '')
            if osp.isdir(path):
                return path
            else:
                path = ''

        if not path:
            raise RuntimeError("Please set the environment variable HOME to "
                               "your user/home directory.")


_home_dir = get_home_dir()


def get_conf_path(subfolder=None, filename=None, create=True):
    """
    Returns the default config path for the platform. This will be:

        - macOS: "~/Library/Application Support/<subfolder>/<filename>."
        - Linux: "XDG_CONFIG_HOME/<subfolder>/<filename>"
        - other: "~/.config/<subfolder>/<filename>"

    :param str subfolder: The subfolder for the app.
    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """
    if platform.system() == "Darwin":
        conf_path = osp.join(_home_dir, "Library", "Application Support")
    else:
        fallback = osp.join(_home_dir, ".config")
        conf_path = os.environ.get("XDG_CONFIG_HOME", fallback)

    # attach subfolder
    if subfolder:
        conf_path = osp.join(conf_path, subfolder)

    # create dir
    if create:
        os.makedirs(conf_path, exist_ok=True)

    # attach filename
    if filename:
        conf_path = osp.join(conf_path, filename)

    return conf_path


def get_log_path(subfolder=None, filename=None, create=True):
    """
    Returns the default log path for the platform. This will be:

        - macOS: "~/Library/Logs/SUBFOLDER/FILENAME"
        - Linux: "$XDG_CACHE_HOME/SUBFOLDER/FILENAME"
        - fallback: "$HOME/.cache/SUBFOLDER/FILENAME"

    :param str subfolder: The subfolder for the app.
    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """

    # if-defs for different platforms
    if platform.system() == "Darwin":
        log_path = osp.join(_home_dir, "Library", "Logs")
    else:
        fallback = osp.join(_home_dir, ".cache")
        log_path = os.environ.get("XDG_CACHE_HOME", fallback)

    # attach subfolder
    if subfolder:
        log_path = osp.join(log_path, subfolder)

    # create dir
    if create:
        os.makedirs(log_path, exist_ok=True)

    # attach filename
    if filename:
        log_path = osp.join(log_path, filename)

    return log_path


def get_cache_path(subfolder=None, filename=None, create=True):
    """
    Returns the default cache path for the platform. This will be:

        - macOS: "~/Library/Application Support/SUBFOLDER/FILENAME"
        - Linux: "$XDG_CACHE_HOME/SUBFOLDER/FILENAME"
        - fallback: "$HOME/.cache/SUBFOLDER/FILENAME"

    :param str subfolder: The subfolder for the app.
    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """
    if platform.system() == "Darwin":
        return get_conf_path(subfolder, filename, create)
    else:
        return get_log_path(subfolder, filename, create)


def get_autostart_path(filename=None, create=True):
    """
    Returns the default path for login items for the platform. This will be:

        - macOS: "~/Library/LaunchAgents/FILENAME"
        - Linux: "$XDG_CONFIG_HOME/autostart/FILENAME"
        - fallback: "$HOME/.config/autostart/FILENAME"

    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """
    if platform.system() == "Darwin":
        autostart_path = osp.join(_home_dir, "Library", "LaunchAgents")
    else:
        autostart_path = get_conf_path("autostart", create=create)

    # attach filename
    if filename:
        autostart_path = osp.join(autostart_path, filename)

    return autostart_path


def get_runtime_path(subfolder=None, filename=None, create=True):
    """
    Returns the default runtime path for the platform. This will be:

        - macOS: tempfile.gettempdir() + "SUBFOLDER/FILENAME"
        - Linux: "$XDG_RUNTIME_DIR/SUBFOLDER/FILENAME"
        - fallback: "$HOME/.cache/SUBFOLDER/FILENAME"

    :param str subfolder: The subfolder for the app.
    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """

    # if-defs for different platforms
    if platform.system() == "Darwin":
        import tempfile
        runtime_path = tempfile.gettempdir()
    else:
        fallback = get_cache_path()
        runtime_path = os.environ.get("XDG_RUNTIME_DIR", fallback)

    # attach subfolder
    if subfolder:
        runtime_path = osp.join(runtime_path, subfolder)

    # create dir
    if create:
        os.makedirs(runtime_path, exist_ok=True)

    # attach filename
    if filename:
        runtime_path = osp.join(runtime_path, filename)

    return runtime_path


def get_state_path(subfolder=None, filename=None, create=True):
    """
    Returns the default path to save application states for the platform. This will be:

        - macOS: "~/Library/Application Support/SUBFOLDER/FILENAME"
        - Linux: "$XDG_DATA_DIR/SUBFOLDER/FILENAME"
        - fallback: "$HOME/.local/share/SUBFOLDER/FILENAME"

    Note: We do not use "~/Library/Saved Application State" on macOS since this folder is
    reserved for user interface state and can be cleared by the user / system.

    :param str subfolder: The subfolder for the app.
    :param str filename: The filename to append for the app.
    :param bool create: If ``True``, the folder "<subfolder>" will be created on-demand.
    """

    # if-defs for different platforms
    if platform.system() == "Darwin":
        state_path = osp.join(_home_dir, "Library", "Application Support")
    else:
        fallback = osp.join(_home_dir, ".local", "share")
        state_path = os.environ.get("$XDG_DATA_DIR", fallback)

    # attach subfolder
    if subfolder:
        state_path = osp.join(state_path, subfolder)

    # create dir
    if create:
        os.makedirs(state_path, exist_ok=True)

    # attach filename
    if filename:
        state_path = osp.join(state_path, filename)

    return state_path
