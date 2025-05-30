#!/bin/bash
# System information script for SkogCLI

echo "=== System Information ==="
echo "Hostname: $(hostname)"
echo "Kernel: $(uname -r)"
echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo

echo "=== CPU Information ==="
echo "CPU Model: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^[ \t]*//')"
echo "CPU Cores: $(grep -c processor /proc/cpuinfo)"
echo

echo "=== Memory Information ==="
free -h
echo

echo "=== Disk Usage ==="
df -h
echo

echo "=== Network Information ==="
ip -br addr show
echo

echo "=== Process Information ==="
echo "Top 5 CPU processes:"
ps aux --sort=-%cpu | head -6
echo
echo "Top 5 Memory processes:"
ps aux --sort=-%mem | head -6
