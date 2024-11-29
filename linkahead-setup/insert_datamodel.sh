#!/bin/bash
# Insert the data model used by the crawler
# A. Schlemmer, 02/2023

python3 -m caosadvancedtools.models.parser --noquestion --sync datamodel.yaml
