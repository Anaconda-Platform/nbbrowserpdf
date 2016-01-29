from argparse import ArgumentParser
# import logging
import time
import os

from ghost import Ghost
from ghost.bindings import (
    QPainter,
    QPrinter,
    QtCore,
)

from PyPDF2 import (
    PdfFileReader,
    PdfFileWriter,
)

from .base import (
    IPYNB_NAME,
    PDF_NAME
)


# a notional default viewport...
VIEWPORT = (1200, 900)


class NotebookPDFGhost(object):
    embed_ipynb = True
    ipynb_name = IPYNB_NAME
    pdf_name = PDF_NAME

    def __init__(self, url, static_path):
        self.url = url
        self.static_path = static_path

        self.ghost = self.init_ghost()
        self.session = self.init_session()

    def init_ghost(self):
        """ Create ghost instance... could be used to customize ghost/qt
            behavior
        """
        return Ghost(
            # log_level=logging.DEBUG
        )

    def init_session(self):
        """ Create a ghost session
        """
        return self.ghost.start(
            # display=True,
            # TODO: read this off config
            viewport_size=VIEWPORT,
            show_scrollbars=False,
            display=True
        )

    def render(self):
        self.session.open(self.url)
        self.page_ready()
        self.print_to_pdf(self.in_static(self.pdf_name))
        self.post_process()

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

        return self.in_static(self.pdf_name)


def main(url, static_path):
    pdf_ghost = NotebookPDFGhost(url, static_path)

    pdf_ghost.render()


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Generate a PDF from a directory of notebook assets")

    parser.add_argument(
        "url",
        help="The url to capture"
    )

    parser.add_argument(
        "static_path",
        help="The directory to generate: must contain an index.html"
    )
    main(**parser.parse_args().__dict__)
