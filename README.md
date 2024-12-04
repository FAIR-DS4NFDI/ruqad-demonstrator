# FAIR Dataspaces RuQaD

RuQaD (Reuse Quality-assured Data) is a demonstrator for connecting and populating FAIR data spaces.
Ruqad connects to [Kadi4Mat](https://kadi.iam.kit.edu/) instances, runs [quality checks](https://git.rwth-aachen.de/fair-ds/ap-4-2-demonstrator/ap-4.2-data-validation-and-quality-assurance-demonstrator) on the data, stores the results
in a [LinkAhead](https://getlinkahead.com) instance and makes the data available via an [EDC (Eclipse Dataspace
Components)](https://projects.eclipse.org/projects/technology.edc) instance.

## Usage

### Installation ###

Simply install with:

`pip install .`

Note: You can safely ignore the `requirements.txt`, this file is used as a lock file for components
analysis.  For more information, look at the section "SCA" below.

### Run locally ###

- Make sure that `qualitycheck_config.toml` and `secrets.sh` are filled with valied values.
- Run `(set -a && . secrets.sh && rq_monitor)`, a short explanation follows:
  - `(...)`: Putting the parentheses prevents pollution of your shell with the variables defined in
    `secrets.sh`.
  - `set -a`: This automatically exports all set variables in the shell.
  - `. secrets.sh`: (Mind the dot `.`) This sources the variables defined in the file.
  - `rq_monitor`: This starts the actual monitor, using the variables defined before.
- To run the service on data, insert new data to the Kadi4Mat instance:
  - Log in to the Kadi server, with an account whose records are visible with the configured token.
  - Create new record.
  - Quickly append a file (for example `abalone.csv` from the *demonstrator4.2* example repo) to the
    record.
  - Wait for the new record with the file to be digested by the Ruqad monitor.

## Development ##

### Unit Tests

- For testing, install with the `test` extra, for example like so: `pip install .[test]`
- Then run `make unittest` or `pytest unittests/`.

### E2E Tests
In order to run the E2E test, you need to create a personal access token (pat) in the public 
[demo instance](https://demo-kadi4mat.iam.kit.edu). You can then run the test as follows:
`KADITOKEN=<token> python -m pytest end-to-end-tests/test_kadi.py`

### Code style and liniting

Run `make style lint` after installing with the `dev` extra.  (The `dev` extra includes the `test`
extra.)

### SCA (Software component analysis) ###

To run the SCA job in the pipeline, run `make bom` and commit the generated `requirements.txt` to
git.  This will be used in the `gemnasium-python-dependency_scanning` job of the `code-analysis`
stage to generate `gl-sbom-pypi-pip.cdx.json` file in CycloneDX format inside the artifacts zip
file.  This file can be visuealized for example with [Dependency Track](https://dependencytrack.org/).

## Docker deployment ##

Ruqad can also be deployed as a container.  More documentation on this is in `docker/`.
