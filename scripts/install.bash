#!/bin/bash
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "${SCRIPT_DIR}/systemd/systemd-install.bash"

: ${EXEC_DESTINATION:="/usr/bin/kynance"}
: ${EXEC_SOURCE:="./scripts/kynance"}

cp_executable_to_usr_bin() {
    cp $EXEC_SOURCE $EXEC_DESTINATION
}

chmod_executbale() {
    chmod +x $EXEC_SOURCE
}

function main() {
    chmod_executbale
    cp_executable_to_usr_bin
    systemd_install
}

main