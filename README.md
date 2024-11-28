# laser-cohorts
Cohort models implemented with the LASER toolkit.

## Setup
Example using [uv](https://github.com/astral-sh/uv):

0. Create and activate virtual environment
```
uv venv
source .venv/bin/activate
```
1. Install
```
uv pip install -e .
```
2. Test that the model runs (`laser --help` for options)
```
laser
```

## Development notes

For linting I find it useful to run:

```bash
uvx pre-commit run --all-file
uvx ruff check
uvx ruff check --fix
```

To run all tests:
```bash
tox
```
