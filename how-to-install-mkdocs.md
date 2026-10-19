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
python3 -m pip install -r requirements-docs.txt
```


## Building and previewing the documentation the easy way

The repository includes a Makefile to simplify local development,
building, and validation of the documentation.

All commands must be executed from the root of the repository.

| Command | Description |
|---|---|
| `make serve` | Start a local development server with live reload. |
| `make build` | Build the complete versioned documentation website. |
| `make validate` | Validate the generated website and version selector. |
| `make preview` | Build and serve the complete website locally. |

### Local development

When writing or updating documentation, run:

```bash
make serve

## Build and validate the complete selector locally the hard way

```bash
python3 tools/build_versioned_site.py \
  --repository . \
  --metadata .github/docs-versions.yml \
  --use-current-checkout \
  --output .build/site \
  --base-url http://localhost:8000/
python3 tools/validate_versioned_site.py \
  .build/site --metadata .github/docs-versions.yml
python3 -m http.server --directory .build/site 8000
```

Open `http://localhost:8000/` and verify all three selector entries. This local
command uses the current checkout for every metadata entry; CI reads the same
file and builds the real branches.

## Some guidelines

To-Do
