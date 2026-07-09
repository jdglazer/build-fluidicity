#!/bin/bash

SCRIPT_DIR=$( dirname "$0" )

docker build --tag buildfluidicitybuilder:latest "$SCRIPT_DIR"