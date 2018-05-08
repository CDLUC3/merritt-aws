# Running

This project assumes [Python 3](https://www.python.org/downloads/) and 
requires [pipenv](https://github.com/pypa/pipenv), both of which can
be installed on a Mac with [Homebrew](https://brew.sh/).

PDF conversion requires [Inkscape](https://inkscape.org/), which can also be installed with 
Homebrew, with [shenanigans](https://inkscape.org/en/download/mac-os/):

```
brew install caskformula/caskformula/inkscape
``` 

To launch the notebook:

```
pipenv shell    # launches a shell with the proper Python environment
pipenv install  # installs packages from Pipfile
jupyter lab     # launches JupyterLab
```
