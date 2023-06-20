#!/bin/bash
set -x

DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source "${DIR}/systemd/systemd-install.bash"

: ${DO_INSTALL_SYSTEMD:=true}
: ${EXEC_DESTINATION:="/usr/bin/kynance"}
: ${SCRIPT_NAME:="earnings.py"}
: ${DIST_PATH:="${DIR}/dist"}
: ${EXEC_NAME:="kynance"}
: ${EXEC_SOURCE:="${DIST_PATH}/${EXEC_NAME}"}

activate_virtual_env() {
    . "${DIR}/venv/bin/activate"
}

run_pyinstaller() {
    pyinstaller --onefile --noconfirm \
                --name "${EXEC_NAME}" \
                --distpath "${DIST_PATH}" \
                "${SCRIPT_NAME}"
}

cp_executable_to_usr_bin() {
    cp $EXEC_SOURCE $EXEC_DESTINATION
}

function main() {
    activate_virtual_env
    run_pyinstaller
    cp_executable_to_usr_bin
    if [ "${DO_INSTALL_SYSTEMD}" == true ]
    then
        systemd_install
    fi
}

main