# flake8: noqa
from ._version import __version__, __version_info__


def load_jupyter_server_extension(nbapp):
    """ Hack the exporter_map to include browser-based PDF
    """
    from nbconvert.exporters.export import exporter_map

    from .exporters import BrowserPDFExporter

    exporter_map.update(
        browserpdf=BrowserPDFExporter
    )
    nbapp.log.debug("Enabling headless browser PDF generation")
