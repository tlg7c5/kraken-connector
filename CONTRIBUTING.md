# Contributing to `kraken-connector`

Contributions are welcome, and they are greatly appreciated!
Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/tlg7c5/kraken-connector/issues

If you are reporting a bug, please include:

- Your operating system name and version.
- Python version and kraken-connector version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs.
Anything tagged with "bug" and "help wanted" is open to whoever wants to implement a fix for it.

### Implement Features

Look through the GitHub issues for features.
Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

`kraken-connector` could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/tlg7c5/kraken-connector/issues.

If you are proposing a new feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions
  are welcome.

## Prerequisites

- Python 3.11 or later
- [PDM](https://pdm-project.org/) for dependency management
- [Git](https://git-scm.com/)

## Get Started

Ready to contribute? Here's how to set up `kraken-connector` for local development.

1. Fork the `kraken-connector` repo on GitHub.

2. Clone your fork locally:

   ```bash
   git clone git@github.com:YOUR_NAME/kraken-connector.git
   cd kraken-connector
   ```

3. Install the environment and pre-commit hooks:

   ```bash
   make install
   ```

   This runs `pdm install` and `pdm run pre-commit install`. If you are using `pyenv`, select a version first:

   ```bash
   pyenv local 3.11
   ```

4. Create a branch for local development:

   ```bash
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

5. Add test cases for your changes to the `tests` directory.

6. Run code quality checks (linting, type checking, dependency audit):

   ```bash
   make check
   ```

7. Run the test suite:

   ```bash
   make test
   ```

8. (Optional) Run tox to test across Python versions. This also runs in CI, so you can skip it locally:

   ```bash
   tox
   ```

9. Commit your changes and push your branch to GitHub:

   ```bash
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

10. Submit a pull request through the GitHub website.

## Serving docs locally

To preview documentation changes:

```bash
make docs
```

This runs `mkdocs serve` and opens a local preview at `http://127.0.0.1:8000`. Changes to doc files are hot-reloaded.

To validate that docs build without errors:

```bash
make docs-test
```

## Code style

- **Formatting**: [Black](https://github.com/psf/black) (line length 88)
- **Linting**: [Ruff](https://github.com/astral-sh/ruff) with a broad rule set (see `pyproject.toml` for details)
- **Type checking**: [mypy](https://mypy-lang.org/) with strict settings (`disallow_untyped_defs`, `disallow_any_unimported`)
- **Docstrings**: Google format

Pre-commit hooks enforce formatting and linting automatically on each commit.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a Google-format docstring.
3. All CI checks (lint, type check, tests) should pass.
