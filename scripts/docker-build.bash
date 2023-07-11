#!/bin/bash

: ${PYTHON_VERSION:="3.9"}
: ${IMG_TAG:="kynance/builder"}
: ${BUILD_PLATFORM:="linux/arm32v7"}

main() {
  docker buildx build . \
        --rm \
        --load \
        -f docker/Dockerfile \
        -t "${IMG_TAG}" \
        --platform "${BUILD_PLATFORM}" \
        --build-arg BUILD_PLATFORM=${BUILD_PLATFORM} \
        "$@";
}

main "$@"