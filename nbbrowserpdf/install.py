#!/usr/bin/env python

import argparse
import os
import subprocess
import sys
from os.path import (
    abspath,
    dirname,
    exists,
    join,
)
try:
    from inspect import signature
except ImportError:
    from funcsigs import signature

from jupyter_core.paths import jupyter_config_dir


def install(enable=False, **kwargs):
    """Install the nbbrowserpdf nbextension assets and optionally enables the
       nbextension and server extension for every run.

    Parameters
    ----------
    enable: bool
        Enable the extension on every notebook launch
    **kwargs: keyword arguments
        Other keyword arguments passed to the install_nbextension command
    """
    from notebook.nbextensions import install_nbextension
    from notebook.services.config import ConfigManager

    directory = join(dirname(abspath(__file__)), 'static', 'nbbrowserpdf')

    kwargs = {k: v for k, v in kwargs.items() if not (v is None)}

    kwargs["destination"] = "nbbrowserpdf"
    install_nbextension(directory, **kwargs)

    if enable:
        if "prefix" in kwargs:
            path = join(kwargs["prefix"], "etc", "jupyter")
            if not exists(path):
                os.makedirs(path)

        cm = ConfigManager(config_dir=path)
        print("Enabling nbbrowserpdf server component in", cm.config_dir)
        cm.update(
            "jupyter_notebook_config", {
                "version": 1,
                "NotebookApp": {
                    "server_extensions": ["nbbrowserpdf"]
                },
            }
        )

        cm = ConfigManager(config_dir=join(jupyter_config_dir(), "nbconfig"))
        print(
            "Enabling nbpresent nbextension at notebook launch in {}".format(
                cm.config_dir
            )
        )
        cm.update(
            "notebook", {
                "load_extensions": {
                    "nbbrowserpdf/index": True
                },
            }
        )


if __name__ == '__main__':
    from notebook.nbextensions import install_nbextension

    install_kwargs = list(signature(install_nbextension).parameters)

    parser = argparse.ArgumentParser(
        description="Installs nbbrowserpdf nbextension")
    parser.add_argument(
        "-e", "--enable",
        help="Automatically load server and nbextension on notebook launch",
        action="store_true")

    default_kwargs = dict(
        action="store",
        nargs="?"
    )

    store_true_kwargs = dict(action="store_true")

    store_true = ["symlink", "overwrite", "quiet", "user"]

    [parser.add_argument(
        "--{}".format(arg),
        **(store_true_kwargs if arg in store_true else default_kwargs)
        )
        for arg in install_kwargs]

    install(**parser.parse_args().__dict__)
