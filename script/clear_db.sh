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

rm -f ../db/*.db && 
rm -f ../static/article/*.md && 
rm -f ../static/image/pfps/* && 
rm -f ../static/image/photos/* && 
rm -f ../static/downloads/* &&
echo "successfully removed database files"
