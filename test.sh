#!/bin/bash

SCRIPT_DIR=$( dirname "$0" )

PYTHONPATH="$SCRIPT_DIR/src" pytest --cov=build_fluidicity_jdglazer --cov-report=html