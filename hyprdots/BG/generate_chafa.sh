#!/bin/bash

# Path to your image
IMAGE_PATH="ca.png"

# Output file for Chafa result
OUTPUT_FILE="ca.txt"

# Run Chafa with desired options
chafa --size=50x30 --symbols=inverted --color-space=din99d --dither=none "$IMAGE_PATH" > "$OUTPUT_FILE"

# Print the path to the output file (optional)
echo "Chafa output saved to: $OUTPUT_FILE"
