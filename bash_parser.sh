#!/bin/bash
# Check if a command-line argument is provided
if [ $# -eq 0 ]; then
    echo "No arguments provided. Please provide the base directory as an argument."
    exit 1
fi

# Define the base directory from the command-line argument
base_dir="$1"

# Iterate over each subdirectory
for subdir in "$base_dir"/*; do
    # Check if it's a directory
    if [ -d "$subdir" ]; then
        # Create "rawdata" subdirectory
        #mkdir -p "$subdir/rawdata"
        
        # Move all files to "rawdata" subdirectory
        #mv "$subdir"/* "$subdir/rawdata"
        
        # Run the python scripts on the subdirectory
        #python ListFiles.py "$subdir" noplot
        python JobLauncher.py -e "$subdir"
    fi
done