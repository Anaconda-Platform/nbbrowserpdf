import os
from argparse import ArgumentParser

from .exporters import (
    APP_ROOT,
    BrowserPDFExporter,
)


def convert(ipynb, pdf):
    exp = BrowserPDFExporter(
        template_file="browserpdf",
        template_path=[os.path.join(APP_ROOT, "templates")]
    )

    output, resources = exp.from_filename(ipynb)

    with open(pdf, "wb+", ) as f:
        f.write(output)


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Convert a notebook to PDF with a headless browser")

    parser.add_argument(
        "ipynb",
        help=".ipynb file to load")

    parser.add_argument(
        "pdf",
        help="PDF to create")

    convert(**parser.parse_args().__dict__)
