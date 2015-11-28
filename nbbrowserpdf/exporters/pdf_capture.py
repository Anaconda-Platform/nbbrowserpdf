import argparse
import os
import logging
import time
from importlib import import_module

try:
    from concurrent import futures
except ImportError:
    import futures

from ghost import Ghost
from ghost.bindings import (
    QPainter,
    QPrinter,
    QtCore,
)

import tornado.web
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor

from PyPDF2 import (
    PdfFileReader,
    PdfFileWriter,
)

import nbformat
from jupyter_core.paths import jupyter_path


# the port on which to serve the fake server
PORT = 9999

# a notional default viewport...
VIEWPORT = (1200, 900)

# the version of the notebook format to use... some autodetect would be nice
IPYNB_VERSION = 4


class CaptureServer(HTTPServer):
    """ A tornado server that handles serving up static HTTP assets. When the
        assets are ready, `capture` is called

        This should be subclassed to provide specific behavior: see
        nbpresent.exporters.pdf_capture (from which this was refactored)
    """
    executor = futures.ThreadPoolExecutor(max_workers=1)
    pdf_name = "notebook.pdf"
    ipynb_name = "notebook.ipynb"
    embed_ipynb = True

    @run_on_executor
    def capture(self):
        """ The main control flow for the capture process.
        """
        self.ghost = self.init_ghost()
        self.session = self.init_session()

        self.session.open("http://localhost:{}/index.html".format(PORT))

        try:
            self.page_ready()
        except Exception as err:
            print(err)

        self.print_to_pdf(self.in_static(self.pdf_name))

        self.post_process()

        raise KeyboardInterrupt()

    def print_to_pdf(self, filename):
        """ Saves page as a pdf file.
            See qt4 QPrinter documentation for more detailed explanations
            of options.
            :param filename: The destination path.
        """

        # TODO: read these from notebook metadata? args?
        paper_size = (8.5, 11.0)
        paper_margins = (0, 0, 0, 0)
        paper_units = QPrinter.Inch
        resolution = 1200

        printer = QPrinter(QPrinter.HighResolution)
        printer.setColorMode(QPrinter.Color)
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setPageMargins(*(paper_margins + (paper_units,)))
        printer.setPaperSize(QtCore.QSizeF(*paper_size), paper_units)
        printer.setResolution(resolution)
        printer.setFullPage(True)

        printer.setOutputFileName(filename)

        # get some sizes for calculations
        nb_width, nb_height = self.selector_size("#notebook")

        # make the screen really long to fit the notebook
        self.session.page.setViewportSize(
            QtCore.QSize(VIEWPORT[0], nb_height + 40)
        )

        body_width, body_height = self.selector_size("body")

        # calculate the native size
        ratio = paper_size[0] / body_width

        # make the page really long to fit the notebook
        printer.setPaperSize(
            QtCore.QSizeF(paper_size[0], nb_height * ratio),
            paper_units)

        painter = QPainter(printer)

        # this is a dark art
        painter.scale(8, 8)

        self.session.main_frame.render(painter)

        painter.end()

    def selector_size(self, selector):
        """ get the screen size of an element
        """
        size, resources = self.session.evaluate(
            """(function(){
                var el = document.querySelector("%s");
                return [el.clientWidth, el.clientHeight];
            })();""" % selector)
        return size

    def in_static(self, *bits):
        """ return a path added to the current static path
        """
        return os.path.join(self.static_path, *bits)

    def init_ghost(self):
        """ Create ghost instance... could be used to customize ghost/qt
            behavior
        """
        return Ghost(
            log_level=logging.DEBUG
        )

    def init_session(self):
        """ Create a ghost session
        """
        return self.ghost.start(
            # display=True,
            # TODO: read this off config
            viewport_size=VIEWPORT,
            show_scrollbars=False,
        )

    def page_ready(self):
        """ A delay to allow for all static assets to be loaded. Some still
            seem to sneak through, thus the additional, hacky 3 second delay.
            On a slow connection, this could *still* create problems.
        """
        self.session.wait_for_page_loaded()
        time.sleep(3)

    def post_process(self):
        """ After the PDF has been created, allow for manipulating the document.
            The default is to embed the ipynb in the PDF.
        """
        if self.embed_ipynb:
            unmeta = PdfFileReader(self.in_static(self.pdf_name), "rb")

            meta = PdfFileWriter()
            meta.appendPagesFromReader(unmeta)

            with open(self.in_static(self.ipynb_name), "rb") as fp:
                meta.addAttachment(self.ipynb_name, fp.read())

            with open(self.in_static(self.pdf_name), "wb") as fp:
                meta.write(fp)


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
    with open(os.path.join(static_path, "notebook.ipynb")) as fp:
        server.notebook = nbformat.read(fp, IPYNB_VERSION)

    ioloop = IOLoop()
    # server.capture will be called when the ioloop is bored for the first time
    ioloop.add_callback(server.capture)
    # connect to a port
    server.listen(PORT)

    try:
        # run forever
        ioloop.start()
    except KeyboardInterrupt:
        # this is probably not the best way to escape, but works for now
        print("Successfully created PDF")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a PDF from a directory of notebook assets")

    parser.add_argument(
        "static_path",
        help="The directory to generate: must contain an index.html"
    )

    parser.add_argument(
        "--capture-server-class",
        help="Alternate server class with entry_point notation, e.g."
             "some.module:ServerClass")

    pdf_capture(**parser.parse_args().__dict__)
