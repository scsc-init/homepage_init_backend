#!/bin/bash

cd "$(dirname "${BASH_SOURCE[0]}")"

rm ../db/*.db && 
rm ../static/article/*.md && 
echo "successfully removed database files"
