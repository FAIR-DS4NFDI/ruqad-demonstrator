# FAIR Dataspaces RuQaD

TODO

## Usage

TODO

### Unit Tests

Run `pytest unittests/`.

### E2E Tests
In order to run the E2E test, you need to create a personal access token (pat) in the public 
[demo instance](https://demo-kadi4mat.iam.kit.edu). You can then run the test as follows:
`KADITOKEN=<token> python -m pytest end-to-end-tests/test_kadi.py`

### Code style and liniting

Run `make style lint` after installing the dependencies listed below.

### Documentation

Run `make doc` after installing the dependencies listed below.

## Dependencies

Package and optional dependencies are declared in the `pyproject.toml`;
additional dependencies for testing are listed in the `tox.ini`.

For linting and code-style we additionally require

- `pylint`

For building the documentation we require

- `sphinx`
- `recommonmark` 
- `sphinx-rtd-theme`
