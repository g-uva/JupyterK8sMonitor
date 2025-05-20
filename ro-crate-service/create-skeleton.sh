#!/bin/bash
# This script creates a skeleton RO-Crate and returns the session ID.
# With this we're able to identify and grab the Session ID from the RO-Crate to identify the folder.
export SESSION_ID=$(python3 create_skeleton.py)
echo $SESSION_ID