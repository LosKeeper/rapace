#!/bin/bash

# This script cleans the topography files
rm "topology/$1.yaml"
cp "topology/${1}_save.yaml" "topology/$1.yaml"
