#!/bin/bash

: ${EXEC_DESTINATION:="/usr/bin/kynance"}
: ${EXEC_SOURCE:="./scripts/kynance"}

cp_executable_to_usr_bin() {
    echo "Copying ${EXEC_SOURCE} to ${EXEC_DESTINATION}"
    cp $EXEC_SOURCE $EXEC_DESTINATION
}

function main() {
    cp_executable_to_usr_bin
}

main