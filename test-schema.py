"""
module description
"""
from importlib import resources

from caoscrawler.validator import load_json_schema_from_datamodel_yaml, validate

ruqad_crawler_settings = resources.files('ruqad').joinpath('resources/crawler-settings')
datamodel_yaml_file = ruqad_crawler_settings.joinpath('datamodel.yaml')
schemas = load_json_schema_from_datamodel_yaml(datamodel_yaml_file)
