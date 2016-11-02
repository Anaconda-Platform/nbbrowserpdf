# nbbrowserpdf
> LaTeX-free PDF generation for Jupyter Notebooks

## Installation
> TODO: pypi package
```shell
pip install https://github.com/Anaconda-Server/nbbrowserpdf/archive/master.zip
python -m nbbrowserpdf.install
```

Enable the extension for every notebook launch:
```shell
python -m nbbrowserpdf.install --enable
```

Installing with `conda` will handle the installation and enabling (in user
space):
```shell
conda install --channel anaconda-nb-extensions nbbrowserpdf
```

## In-Browser Usage
In the Notebook application menu bar, click in **File** -> **Download As...**
-> **PDF via Headless Browser (.pdf)**.

## CLI
You can generate a PDF at the command line:
```shell
nbbrowserpdf -i Notebook.ipynb -o Notebook.pdf
```

`nbbrowserpdf` will also work with streams
```shell
cmd_that_makes_ipynb | nbbrowserpdf > output.pdf
```

You can also see the whole documentation
```shell
nbbrowserpdf --help
```

## Development
> TODO: document development processes
