#!/bin/bash

# Calculate average CPU usage
# Read /proc/stat twice with a short interval
CPU1=($(awk '/^cpu / {print $2, $3, $4, $5, $6, $7, $8, $9, $10, $11}' /proc/stat))
sleep 1
CPU2=($(awk '/^cpu / {print $2, $3, $4, $5, $6, $7, $8, $9, $10, $11}' /proc/stat))

# Calculate the difference
IDLE1=${CPU1[3]}
IDLE2=${CPU2[3]}
TOTAL1=0
TOTAL2=0

for VALUE in "${CPU1[@]}"; do
  TOTAL1=$((TOTAL1 + VALUE))
done

for VALUE in "${CPU2[@]}"; do
  TOTAL2=$((TOTAL2 + VALUE))
done

IDLE=$((IDLE2 - IDLE1))
TOTAL=$((TOTAL2 - TOTAL1))
DIFF=$((TOTAL - IDLE))

CPU_USAGE=$((100 * DIFF / TOTAL))

# Get average CPU temperature
CPU_TEMP=$(sensors | awk '/Core [0-9]+/ {sum += $3; count++} END {if (count > 0) printf("%.0f", sum / count); else print "N/A"}')

echo "CPU: $CPU_USAGE % [ $CPU_TEMP °C ]"
