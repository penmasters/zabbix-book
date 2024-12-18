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

```zsh
pip3 install --upgrade pip
```

## Install MkDocs

```zsh
pip3 install mkdocs
```

## Install MkDocs extension material

```zsh
pip3 install mkdocs-material
```

## Install MkDocs extension with-pdf

```
pip3 install mkdocs-print-site-plugin
```

## Install MkDocs support for multi language

```
pip3 install mkdocs-static-i18n
```
## Install the spellcheck 

pip3 install 'mkdocs-spellcheck[all]'


## Build your site local and test it

```
python3 -m mkdocs serve
```

```
python3 -m mkdocs build
```

## Some guidlines

To-Do
