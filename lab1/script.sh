#!/bin/bash

# Prints even numbered lines of each file in current directory
# <Filename>: <line>

for file in *; do
    if [ -f "$file" ]; then # Checks if regular file not directory, etc...
        count=0
        while IFS= read -r line; do
            if (( count % 2 == 1)); then
                echo"$file: $line"
            fi
            ((counter++))
        done < "$file"
    fi
done
