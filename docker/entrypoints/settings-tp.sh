#!/usr/bin/env bash
source utils.sh

VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})

settings-tp -C tcp://${VALIDATOR_ALIAS}:${VALIDATOR_PORT}
