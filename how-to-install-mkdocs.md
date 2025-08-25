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

## Install pip3

```
pip3 install --upgrade pip3
```

## Install MkDocs and extensions

```bash
pip3 install mkdocs
pip3 install mkdocs-material
pip3 install mkdocs-print-site-plugin
pip3 install mkdocs-static-i18n
pip3 install 'mkdocs-spellcheck[all]'
pip3 install mkdocs-autolinks-plugin
pip3 install mkdocs-mermaid2-plugin
```

## Install extra pip3 packages

```
pip3 install idna
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
