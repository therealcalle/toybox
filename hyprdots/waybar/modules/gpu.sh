#!/bin/bash

# Define colors to match the theme
GPU_COLOR="#00E5FF"  # cyan
TEMP_COLOR="#FFB300"  # gold

# Query gpu data
QUERY=$(nvidia-smi --query-gpu=utilization.memory,temperature.gpu --format=csv,noheader,nounits)

# Extract data from query
USAGE=$(echo $QUERY | awk -F, '{print $1}')
TEMP=$(echo $QUERY | awk -F, '{print $2}' | tr -d ' ')

# Output with colored spans
echo "{\"text\": \"<span color='$GPU_COLOR'>$USAGE%</span> | <span color='$TEMP_COLOR'>$TEMP°C</span>\", \"alt\": \"$USAGE\", \"tooltip\": \"GPU Usage: $USAGE%\\nTemp: $TEMP°C\", \"class\": \"gpu\"}"
