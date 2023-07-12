#!/bin/bash

log_file=$LOG_FILE yq -i '.handlers.simple_file.filename = env(log_file)' log/config.yml