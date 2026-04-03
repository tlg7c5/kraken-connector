# Installation

## Requirements

- Python 3.11 or later

## Install from PyPI

```bash
pip install kraken-connector
```

## Dependencies

kraken-connector pulls in three runtime dependencies:

| Package                                          | Purpose                                  |
| ------------------------------------------------ | ---------------------------------------- |
| [httpx](https://www.python-httpx.org/)           | HTTP transport for REST API calls        |
| [websockets](https://websockets.readthedocs.io/) | WebSocket transport for streaming        |
| [attrs](https://www.attrs.org/)                  | Data classes for request/response models |

## Development install

If you want to contribute or run tests locally, clone the repo and use [PDM](https://pdm-project.org/):

```bash
git clone https://github.com/tlg7c5/kraken-connector.git
cd kraken-connector
make install
```

This installs the package in editable mode with dev dependencies and sets up pre-commit hooks. See [Contributing](../contributing.md) for the full development workflow.
