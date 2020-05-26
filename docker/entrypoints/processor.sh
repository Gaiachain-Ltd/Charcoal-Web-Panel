#!/usr/bin/env bash
source /utils.sh

VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})

python3 /app/main.py -C tcp://${VALIDATOR_IP}:${VALIDATOR_PORT}
