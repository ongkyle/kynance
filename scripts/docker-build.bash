#!/bin/bash

: ${PYTHON_VERSION:="3.10"}
: ${DEBIAN_VERSION:="buster"}
: ${IMG_TAG:=""}

main() {
  docker build . \
        --rm \
        -f docker/Dockerfile \
        --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
        --build-arg DEBIAN_VERSION=${DEBIAN_VERSION} \
        "$@";
}

main "$@"