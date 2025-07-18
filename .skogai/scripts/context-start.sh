#!/usr/bin/env bash
set -e
printf "[@claude:context:%s](generated: %s)\n" "$1" "$(date)"
