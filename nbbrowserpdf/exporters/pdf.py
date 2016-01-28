import os
from os.path import (
    join,
)
import shutil
import subprocess
import sys

from ipython_genutils.tempdir import TemporaryWorkingDirectory
import nbformat

from nbconvert.exporters.html import HTMLExporter

from .base import (
    HTML_NAME,
    IPYNB_NAME,
    PDF_NAME,
)


class BrowserPDFExporter(HTMLExporter):
    """ An exporter that generates PDF with a headless browser.
        Heavily influenced by the nbconvert LaTeX-based PDFExporter.
    """
    html_name = HTML_NAME
    ipynb_name = IPYNB_NAME
    pdf_name = PDF_NAME

    def pdf_capture_args(self):
        """ extra arguments to pass to pdf_capture... such as
            --capture-server-class
        """
        return []

    def from_notebook_node(self, nb, resources=None, **kw):
        """ Generate a PDF from a given parsed notebook node
        """
        output, resources = super(BrowserPDFExporter, self).from_notebook_node(
            nb, resources=resources, **kw
        )

        with TemporaryWorkingDirectory() as tmpdir:
            for path, res in resources.get("outputs", {}).items():
                dest = join(tmpdir, os.path.basename(path))
                shutil.copyfile(path, dest)

            with open(join(tmpdir, self.html_name), "w+") as fp:
                fp.write(output)

            with open(join(tmpdir, self.ipynb_name), "w") as fp:
                nbformat.write(nb, fp)

            subprocess.check_call([
                sys.executable,
                "-m", "nbbrowserpdf.exporters.pdf_capture",
                tmpdir
            ] + self.pdf_capture_args())

            if not os.path.isfile(self.pdf_name):
                raise IOError("PDF creating failed")

            self.log.info("PDF successfully created")

            with open(self.pdf_name, 'rb') as f:
                pdf_data = f.read()

        resources['output_extension'] = '.pdf'

        # clear figure outputs, extracted by pdf export,
        # so we don't claim to be a multi-file export.
        resources.pop('outputs', None)

        return pdf_data, resources
