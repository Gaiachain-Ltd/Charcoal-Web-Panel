#!/usr/bin/env bash
source /utils.sh

VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})

python3 manage.py runsyncserver -C tcp://${VALIDATOR_ALIAS}:${VALIDATOR_PORT}