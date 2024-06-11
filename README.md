# LinkAhead Python Package Template

This Repo serves as a template for LinkAhead related Python packages, e.g.,
custom crawler converters.

## Usage

To create a new Python package, fork this repo and change the names in the `src`
directory, `pyproject.toml`, `Makefile`, `src/doc/Makefile`, `src/doc/conf.py`
and `tox.ini`. Also edit the `authors` field therein. If applicable, create a
`citation.cff` for the new project.

Also update this `README.md` to contain actual package information including
license, copyright, conttributors, etc. See [Pylib's
README.md](https://gitlab.com/linkahead/linkahead-pylib/-/blob/main/README.md?ref_type=heads)
as an example.

Then, write your Python code in `/src/<package_name>`, and add unit tests in
`unittests`. Documentation goes to `/src/doc`.

If you want to publish the result on PyPi, there is a release.sh helper
script. Make sure that your `pyproject.toml` contains the correct and complete
metadata and check the `RELEASE_GUIDELINES.md`

### Unit Tests

Run `tox` or alternatively `pytest unittests/`.

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
