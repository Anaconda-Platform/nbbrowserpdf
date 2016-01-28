# nbbrowserpdf
> LaTeX-free PDF generation for Jupyter Notebooks

## Installation
### `pip`
```shell
pip install nbbrowserpdf
python -m nbbrowserpdf.install
```

Enable the extension for every notebook launch:
```shell
python -m nbpresent.install --enable
```

### `conda`
```shell
conda install --channel nbcio nbbrowserpdf
```
Installing with `conda` will handle the installation and enabling in your conda
environment.


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
