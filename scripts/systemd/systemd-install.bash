#!/bin/bash
set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

: ${TIMER_LOCATION:="${SCRIPT_DIR}/kynance.timer"}
: ${SERVICE_LOCATION:="${SCRIPT_DIR}/kynance.service"}
: ${TIMER_NAME:="kynance.timer"}
: ${SERVICE_NAME:="kynance.service"}
: ${SYSTEMD_DIR:="/etc/systemd/system/"}
: ${TIMER_DIR:="/etc/systemd/kynance.timer"}

cp_timer_to_systemd() {
    cp $TIMER_LOCATION $SYSTEMD_DIR
}

cp_service_to_systemd() {
    cp $SERVICE_LOCATION $SYSTEMD_DIR
}

enable_timer() {
  systemctl enable "${TIMER_NAME}"
}

start_timer() {
  systemctl start "${TIMER_NAME}"
}

show_timer_status() {
  systemctl status "${TIMER_NAME}"
}

systemd_install() {
  cp_timer_to_systemd
  cp_service_to_systemd
  enable_timer
  start_timer
  show_timer_status
}
