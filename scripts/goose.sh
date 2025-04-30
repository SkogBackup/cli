#!/bin/bash
# Agent script for goose
# This file is managed by skogcli - manual changes may be overwritten

# Execute the agent command
# Don't use bash to execute a binary file
/home/skogix/.skogai/agents/goose-src/target/release/goose run --text '{message}'
