#!/bin/bash

SCRIPT_DIR=$( dirname $0 )
docker run -it -v "$SCRIPT_DIR:/build-fluidicity" buildfluidicitybuilder:latest