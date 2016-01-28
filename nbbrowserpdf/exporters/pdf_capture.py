import argparse
import os
import sys
import subprocess
from importlib import import_module

try:
    from concurrent import futures
except ImportError:
    import futures


import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
from tornado.log import enable_pretty_logging

import nbformat
from jupyter_core.paths import jupyter_path

from .base import (
    HTML_NAME,
    IPYNB_NAME,
)

ADDRESS = "127.0.0.1"

# the version of the notebook format to use... some autodetect would be nice
IPYNB_VERSION = 4


class WorkCompleteInterrupt(KeyboardInterrupt):
    """ For some reason, only KeyboardInterrupt works cross-platform to kill
        tornado from inside. Probably bad.
    """
    pass


class CaptureServer(HTTPServer):
    """ A tornado server that handles serving up static HTTP assets. When the
        assets are ready, `capture` is called

        This should be subclassed to provide specific behavior: see
        nbpresent.exporters.pdf_capture (from which this was refactored)
    """
    executor = futures.ThreadPoolExecutor(max_workers=1)
    ghost_class = "nbbrowserpdf.exporters.pdf_ghost"

    @property
    def capture_url(self):
        return "http://{1}:{2}/{0}".format(
            HTML_NAME,
            *list(self._sockets.values())[0].getsockname())

    @run_on_executor
    def capture(self):
        """ Fire off the capture subprocess, then shut down the server
        """
        subprocess.Popen([
            sys.executable, "-m", self.ghost_class,
            self.capture_url,
            self.static_path
        ], stdout=subprocess.PIPE).communicate()

        raise WorkCompleteInterrupt()


def pdf_capture(static_path, capture_server_class=None):
    """ Starts a tornado server which serves all of the jupyter path locations
        as well as the working directory
    """
    settings = {
        "static_path": static_path
    }

    handlers = [
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": settings['static_path']
        })
    ]

    # add the jupyter static paths
    for path in jupyter_path():
        handlers += [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {
                "path": os.path.join(path, "static")
            })
        ]

    app = tornado.web.Application(handlers, **settings)

    if capture_server_class is None:
        server = CaptureServer(app)
    else:
        _module, _klass = capture_server_class.split(":")
        server = getattr(import_module(_module), _klass)(app)

    # can't pass this to the constructor for some reason...
    server.static_path = static_path

    # add the parsed, normalized notebook
    with open(os.path.join(static_path, IPYNB_NAME)) as fp:
        server.notebook = nbformat.read(fp, IPYNB_VERSION)

    ioloop = IOLoop()
    # server.capture will be called when the ioloop is bored for the first time
    ioloop.add_callback(server.capture)
    # connect to a port
    server.listen(port=0, address=ADDRESS)

    try:
        ioloop.start()
    except WorkCompleteInterrupt:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a PDF from a directory of notebook assets")

    parser.add_argument(
        "static_path",
        help="The directory to generate: must contain an {}".format(HTML_NAME)
    )

    parser.add_argument(
        "--capture-server-class",
        help="Alternate server class with entry_point notation, e.g."
             "some.module:ServerClass")

    pdf_capture(**parser.parse_args().__dict__)
