import subprocess
from os.path import (
    dirname,
    join
)

here = dirname(__file__)


def test_cli():
    proc = subprocess.Popen([
        "nbbrowserpdf",
        "-i", join(here, "notebooks", "Test.ipynb"),
        "-o", "Test.pdf"
    ], stderr=subprocess.PIPE)
    print(proc.communicate()[1].decode())
    assert proc.returncode == 0
