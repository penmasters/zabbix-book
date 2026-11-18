# How to install MkDocs on OSX

This explains how to set up MkDocs on your Mac so that you can pull changes
from Git and run the web server locally.

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
python3 -m pip install --upgrade pip
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
| `make preview` | Serve the previously built website locally. |

### Local development

When writing or updating documentation, run:

```bash
make serve
```

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

Open `http://localhost:8000/` and verify all enabled selector entries. This local
command uses the current checkout for every enabled metadata entry; CI reads the same
file and builds the real branches.

## Some guidelines

To-Do
