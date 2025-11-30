#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "WARNING: This will delete all database files, articles, and images!"

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

rm ../db/*.db && 
rm -r ../static/ &&
echo "successfully removed database files"
