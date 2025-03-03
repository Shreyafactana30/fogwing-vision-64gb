#!/bin/bash

# This script sets up the required environment by installing necessary packages.

# Ensure the script is executed with /bin/bash
if [ -z "$BASH_VERSION" ]; then
  exec /bin/bash "$0" "$@"
fi


# Check if the 'models' directory exists before cloning.
if [ ! -d "models" ]; then
  # Cloning project directory from TF Model Garden for postprocessing
  # and preprocessing functions.
  git clone --depth 1 https://github.com/tensorflow/models.git
else
  echo "'models' directory already exists. Skipping cloning."
fi

