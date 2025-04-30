#!/bin/bash
# Agent script for goose
# This file is managed by skogcli - manual changes may be overwritten

# Execute the agent command
/home/skogix/.skogai/agents/goose-src/target/release/goose run --text '{message}'
