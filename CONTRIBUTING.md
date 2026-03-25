# Contributing to `kraken-connector`

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

You can contribute in many ways:

# Types of Contributions

## Report Bugs

Report bugs at https://github.com/tlg7c5/kraken-connector/issues

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

## Fix Bugs

Look through the GitHub issues for bugs.
Anything tagged with "bug" and "help wanted" is open to whoever wants to implement a fix for it.

## Implement Features

Look through the GitHub issues for features.
Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

## Write Documentation

Cookiecutter PyPackage could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

## Submit Feedback

The best way to send feedback is to file an issue at https://github.com/tlg7c5/kraken-connector/issues.

If you are proposing a new feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome :)

# Get Started!

Ready to contribute? Here's how to set up `kraken-connector` for local development.
Please note this documentation assumes you already have `pdm` and `Git` installed and ready to go.

1. Fork the `kraken-connector` repo on GitHub.

2. Clone your fork locally:

```bash
cd <directory_in_which_repo_should_be_created>
git clone git@github.com:YOUR_NAME/kraken-connector.git
```

3. Now we need to install the environment. Navigate into the directory

```bash
cd kraken-connector
```

If you are using `pyenv`, select a version to use locally. (See installed versions with `pyenv versions`)

```bash
pyenv local <x.y.z>
```

Then, install the environment with:

```bash
pdm install
```

4. Install pre-commit to run linters/formatters at commit time:

```bash
pdm run pre-commit install
```

5. Create a branch for local development:

```bash
git checkout -b name-of-your-bugfix-or-feature
```

Now you can make your changes locally.

6. Don't forget to add test cases for your added functionality to the `tests` directory.

7. When you're done making changes, check that your changes pass the formatting tests.

```bash
make check
```

Now, validate that all unit tests are passing:

```bash
make test
```

9. Before raising a pull request you should also run tox.
   This will run the tests across different versions of Python:

```bash
tox
```

This requires you to have multiple versions of python installed.
This step is also triggered in the CI/CD pipeline, so you could also choose to skip this step locally.

10. Commit your changes and push your branch to GitHub:

```bash
git add .
git commit -m "Your detailed description of your changes."
git push origin name-of-your-bugfix-or-feature
```

11. Submit a pull request through the GitHub website.

# Code Generation

The API client and schema classes were initially generated from Kraken's OpenAPI specification using `openapi-python-client`.

## Obtaining the OpenAPI spec

Kraken publishes their REST API spec at https://docs.kraken.com/api/. Save it as `openapi.json` in the repository root (this file is gitignored).

## Regenerating

```bash
make generate
```

This runs `openapi-python-client update --path openapi.json`. The tool is listed as a dev dependency in `pyproject.toml`.

## Manual edits applied post-generation

The generated code serves as scaffolding. The following manual changes have been applied on top and must be reapplied after any regeneration:

1. **KrakenAPIError wiring** — All 48 endpoint `_parse_response()` functions check the response body's `error` field and raise `KrakenAPIError` if non-empty. The generated code does not include this.
2. **HMAC authentication** (`kraken_connector/security.py`) — `sign_message()` and `get_nonce()` are entirely hand-written; they are not part of the generated output.
3. **HTTP client auth logic** (`kraken_connector/http.py`) — `HTTPAuthenticatedClient` injects `API-Key` headers and HMAC signatures. The generated client only handles unauthenticated requests.
4. **Module name shortening** — Some generated module names were shortened for readability.
5. **Model reuse across modules** — Some generated schema classes were consolidated to reduce duplication.
6. **API version prefix constant** (`kraken_connector/constants/api.py`) — Endpoint URLs use `API_VERSION_PREFIX` instead of a hardcoded `/0/` path.
7. **Dead code removal** — Unreachable `pass` statements in `_get_kwargs()` functions were removed.

# Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.

2. If the pull request adds functionality, the docs should be updated.
   Put your new functionality into a function with a docstring, and add the feature to the list in `README.md`.
