# How to install MkDocs on OSX

This explains how to setup MkDocs on your Mac so that you can pull git on your pc and run the webserver local

## make sure brew is installed

```zsh
brew --version
```

## Install python 3 and pango library

```zsh
brew install python3
brew install pango
```

## Install pip

```
pip install --upgrade pip
```

## Install MkDocs and extensions

```bash
pip install mkdocs
pip install mkdocs-material
pip install mkdocs-print-site-plugin
pip install mkdocs-static-i18n
pip install 'mkdocs-spellcheck[all]'
pip install mkdocs-autolinks-plugin
```

## Install extra pip packages

```
pip install idna
```

```
```

## Build your site local and test it

```
python3 -m mkdocs serve
python3 -m mkdocs build
```

## Some guidelines

To-Do
