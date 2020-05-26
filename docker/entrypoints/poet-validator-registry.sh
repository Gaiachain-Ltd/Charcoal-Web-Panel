#!/usr/bin/env bash
source utils.sh

VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})

poet-validator-registry-tp -C tcp://${VALIDATOR_IP}:${VALIDATOR_PORT}

