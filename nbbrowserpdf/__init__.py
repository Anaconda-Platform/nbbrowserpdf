# flake8: noqa
from ._version import __version__, __version_info__


BrowserPDFExporter = None
pdf_import_error = None

try:
    from .exporters.pdf import BrowserPDFExporter
except Exception as err:
    pdf_import_error = err


def load_jupyter_server_extension(nbapp):
    """ Hack the exporter_map to include browser-based PDF
    """
    from nbconvert.exporters.export import exporter_map

    if pdf_import_error:
        nbapp.log.warn(
            "✗ nbbrowserpdf PDF export DISABLED: {}"
            .format(pdf_import_error)
        )
    else:
        nbapp.log.info("✓ nbbrowserpdf PDF export ENABLED")
        exporter_map.update(
            browserpdf=BrowserPDFExporter
        )
