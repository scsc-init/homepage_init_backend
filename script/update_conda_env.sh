#!/bin/bash

# Check if environment name is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <conda-environment-name>"
  echo "Error: No Conda environment name provided. Exiting."
  exit 1
fi

ENV_NAME="$1"
ENV_YML="environment.yml"
REQ_TXT="requirements.txt"

# Check if the Conda environment exists
if ! conda info --envs | awk '{print $1}' | grep -qx "$ENV_NAME"; then
  echo "Error: Conda environment '$ENV_NAME' does not exist. Exiting."
  exit 1
fi

# Export the Conda environment to environment.yml
echo "Exporting Conda environment '$ENV_NAME' to $ENV_YML..."
conda env export -n "$ENV_NAME" --no-builds | grep -v "prefix:" > "$ENV_YML"

# Export pip packages to requirements.txt
echo "Exporting pip requirements from '$ENV_NAME' to $REQ_TXT..."
conda run -n "$ENV_NAME" pip freeze > "$REQ_TXT"

echo "Environment export complete."
