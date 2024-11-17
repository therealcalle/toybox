#!/bin/bash

# Define your colors here - easy to change!
CPU_COLOR="#31fffc"
TEMP_COLOR="#f7b11e"

# Get CPU temperature (adjust 'Package id 0' as per your sensors output)
temp=$(sensors | grep 'Package id 0' | awk '{print $4}' | tr -d '+°C')

# Get CPU usage from /proc/stat
prev_total=0
prev_idle=0

read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
prev_total=$((user + nice + system + idle + iowait + irq + softirq + steal))
prev_idle=$((idle + iowait))

sleep 0.5

read cpu user nice system idle iowait irq softirq steal guest guest_nice < /proc/stat
total=$((user + nice + system + idle + iowait + irq + softirq + steal))
idle=$((idle + iowait))

total_diff=$((total - prev_total))
idle_diff=$((idle - prev_idle))
cpu_usage=$((100 * (total_diff - idle_diff) / total_diff))

# Simpler output for testing
echo "{\"text\": \"<span color='$CPU_COLOR'>$cpu_usage%</span> | <span color='$TEMP_COLOR'>$temp°C</span>\", \"alt\": \"$cpu_usage\", \"tooltip\": \"Average CPU: $cpu_usage%\\nTemp: $temp°C\", \"class\": \"cpu\"}"