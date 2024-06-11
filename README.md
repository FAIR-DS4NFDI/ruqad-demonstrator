# LinkAhead Python Package Template

This Repo serves as a template for LinkAhead related Python packages, e.g.,
custom crawler converters.

## Usage

To create a new Python package, fork this repo and change the names in the `src`
directory, `pyproject.toml`, `setup.cfg`. Also edit the `authors` field
therein. If applicable, create a `citation.cff` for the new project.

Then, write your Python code in `/src/<package_name>`, and add unit tests in
`unittests`. Documentation goes to `/src/doc`.
