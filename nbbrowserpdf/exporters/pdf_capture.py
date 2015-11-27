import os
import logging
import time
import sys

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
import jupyter_core

# the port on which to serve the fake server
PORT = 9999
VIEWPORT = (1200, 900)


class CaptureServer(HTTPServer):
    executor = futures.ThreadPoolExecutor(max_workers=1)
    pdf_name = "notebook.pdf"
    ipynb_name = "notebook.ipynb"
    embed_ipynb = True

    def __init__(self, *args, **kwargs):
        super(CaptureServer, self).__init__(*args, **kwargs)

    def init_ghost(self):
        return Ghost(
            log_level=logging.DEBUG
        )

    def init_session(self):
        return self.ghost.start(
            # display=True,
            # TODO: read this off config
            viewport_size=VIEWPORT,
            show_scrollbars=True,
        )

    def page_ready(self):
        self.session.wait_for_page_loaded()
        time.sleep(1)

    def post_process(self):
        if self.embed_ipynb:
            join = lambda *bits: os.path.join(self.static_path, *bits)

            unmeta = PdfFileReader(join(self.pdf_name), "rb")

            meta = PdfFileWriter()
            meta.appendPagesFromReader(unmeta)

            with open(join(self.ipynb_name), "rb") as fp:
                meta.addAttachment(self.ipynb_name, fp.read())

            with open(join("notebook.pdf"), "wb") as fp:
                meta.write(fp)

    @run_on_executor
    def capture(self):
        self.ghost = self.init_ghost()
        self.session = self.init_session()

        self.session.open("http://localhost:9999/index.html")

        try:
            self.page_ready()
        except Exception as err:
            print(err)

        self.print_to_pdf(self.pdf_name)

        self.post_process()

        raise KeyboardInterrupt()

    def selector_size(self, selector):
        # get some sizes for calculations
        size, resources = self.session.evaluate(
            """(function(){
                var el = $("%s")[0];
                return [el.clientWidth, el.clientHeight];
            })();""" % selector)
        return size

    def print_to_pdf(self, path):
        """Saves page as a pdf file.
        See qt4 QPrinter documentation for more detailed explanations
        of options.
        :param path: The destination path.
        :param paper_size: A 2-tuple indicating size of page to print to.
        :param paper_margins: A 4-tuple indicating size of each margin.
        :param paper_units: Units for pager_size, pager_margins.
        :param zoom_factor: Scale the output content.
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

        printer.setOutputFileName(path)

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


def pdf_capture(static_path):
    settings = {
        "static_path": static_path
    }

    handlers = []

    # add the jupyter static paths
    for path in jupyter_core.paths.jupyter_path():
        handlers += [
            (r"/static/(.*)", tornado.web.StaticFileHandler, {
                "path": os.path.join(path, "static")
            })
        ]

    handlers += [(r"/(.*)", tornado.web.StaticFileHandler, {
        "path": settings['static_path']
    })]

    app = tornado.web.Application(handlers, **settings)

    server = CaptureServer(app)
    server.static_path = static_path

    with open(os.path.join(static_path, "notebook.ipynb")) as fp:
        server.notebook = nbformat.read(fp, 4)

    ioloop = IOLoop()
    ioloop.add_callback(server.capture)
    server.listen(9999)

    try:
        ioloop.start()
    except KeyboardInterrupt:
        print("Successfully created PDF")


if __name__ == "__main__":
    pdf_capture(sys.argv[1])
