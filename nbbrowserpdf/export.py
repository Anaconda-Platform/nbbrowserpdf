from argparse import ArgumentParser
import os
import sys

from .exporters import BrowserPDFExporter

APP_ROOT = os.path.join(os.path.dirname(__file__))


def export(ipynb=None, outfile=None):
    exp = BrowserPDFExporter(
        template_file="browserpdf",
        template_path=[os.path.join(APP_ROOT, "templates")]
    )
    if ipynb is not None:
        output, resources = exp.from_filename(ipynb)
    else:
        output, resources = exp.from_file(sys.stdin)

    if outfile is not None:
        with open(outfile, "wb+") as f:
            f.write(output)
    else:
        sys.stdout.buffer.write(output)


def main():
    parser = ArgumentParser(
        description="Generate a PDF as from a Jupyter Notebook with ghost.py")
    parser.add_argument(
        "-i", "--ipynb",
        help="Input file (otherwise read from stdin)")
    parser.add_argument(
        "-o", "--outfile",
        help="Output file (otherwise write to stdout)")

    export(**parser.parse_args().__dict__)


if __name__ == "__main__":
    main()
