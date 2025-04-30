#!/bin/bash
# Agent script for goose
# This file is managed by skogcli - manual changes may be overwritten

# Execute the agent command
# $1 is the message parameter passed to the script
/home/skogix/.skogai/agents/goose-src/target/release/goose run --text "$1"
