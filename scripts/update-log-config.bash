#!/bin/bash

set -x

: ${LOG_CONFIG_FILE:?LOG_CONFIG_FILE must be set}
: ${LOG_FILE:?LOG_FILE must be set}

log_file=$LOG_FILE yq -i '.handlers.simple_file.filename = env(log_file)' "${LOG_CONFIG_FILE}"