#!/bin/bash
# Agent script for amy
# This file is managed by skogcli - manual changes may be overwritten

# Execute the agent command
# $1 is the message parameter passed to the script
aichat --agent amy -- "$1"
