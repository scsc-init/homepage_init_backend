#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "WARNING: This will delete all database files and the entire static directory!"

while [[ true ]]; do
    read -p "Are you sure you want to continue? (yes/no): " confirm
    if [[ "$confirm" == "no" ]]; then
        echo "Aborted."
        exit 1
    elif [[ "$confirm" != "yes" ]]; then
        echo "Please type 'yes' or 'no'"
    else
        break
    fi
done

rm ../db/*.db || { echo "Failed to remove database files"; exit 1; }
rm -r ../static/ || { echo "Failed to remove static directory"; exit 1; }
echo "Successfully removed database files and static directory"
