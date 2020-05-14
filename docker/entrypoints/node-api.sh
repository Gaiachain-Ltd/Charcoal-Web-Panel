#!/usr/bin/env bash
source utils.sh

VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})
API_IP=$(get_ip ${API_HOST})

sawtooth-rest-api -vv \
    --connect tcp://${VALIDATOR_ALIAS}:${VALIDATOR_PORT} \
    --bind ${API_IP}:${API_PORT}
