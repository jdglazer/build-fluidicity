#!/bin/bash

SCRIPT_DIR=$( dirname "$0" )

usage() {
  echo "Usage: $0 [options]"
  echo "  -h, --help          print this usage message"
  echo "  -i, --dockerimage   build docker image"
  echo "  -r, --runcontainer  run docker container bash command line"
  echo "  -t, --test          run python tests"
  echo "  -b, --build         run python package build"
  echo "  -c, --clean         clean docker system cache (docker prune)"
}

run_on_docker_bash() {
    docker run -it \
         -v "$SCRIPT_DIR:/build-fluidicity" \
         buildfluidicitybuilder:latest -c "$1"
}

if [ -z "$1" ]; then
  usage
  exit 1
fi

while [[ $# -gt 0 ]]; do
  case $1 in
    -h|--help)
      usage
      exit 0
      ;;
    -i|--dockerimage)
      echo "Building docker image..."
      docker build --tag buildfluidicitybuilder:latest "$SCRIPT_DIR"
      shift
      ;;
    -r|--runcontainer)
      echo "Running bash on docker container..."
      exec docker run -it \
                  -v "$SCRIPT_DIR:/build-fluidicity" \
                  buildfluidicitybuilder:latest
      ;;
    -t|--test)
      echo "Running python tests..."
      run_on_docker_bash "PYTHONPATH=src pytest --log-cli-level=DEBUG --cov=build_fluidicity_jdglazer --cov-report=html"
      shift
      ;;
    -b|--build)
      echo "Running python build..."
      run_on_docker_bash "/usr/local/bin/python -m build --no-isolation"
      shift
      ;;
    -c|--clean)
      docker system prune --all
      shift
      ;;
    *)
      usage
      exit 1
      ;;
  esac
done

exit 0