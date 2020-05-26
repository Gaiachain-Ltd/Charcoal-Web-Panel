#!/usr/bin/env bash
source utils.sh

create_config () {
    if [[ ! -f /poet-shared/poet-enclave-measurement ]]; then
        poet enclave measurement >> /poet-shared/poet-enclave-measurement;
    fi

    if [[ ! -f /poet-shared/poet-enclave-basename ]]; then
        poet enclave basename >> /poet-shared/poet-enclave-basename;
    fi

    if [[ ! -f /poet-shared/simulator_rk_pub.pem ]]; then
        cp /etc/sawtooth/simulator_rk_pub.pem /poet-shared;
    fi
}

get_validator_key () {
    while [[ ! -f /poet-shared/validator/keys/validator.priv ]]; do
        sleep 1;
    done

    cp -a /poet-shared/validator/keys /etc/sawtooth
}

register_poet () {
    poet registration create -k /etc/sawtooth/keys/validator.priv -o /poet-shared/poet.batch
}


VALIDATOR_IP=$(get_ip ${VALIDATOR_HOST})

get_validator_key

if [[ -z "${PEERS}" ]]; then
    # If no peers defined, consider is first node which create network.
    create_config
    register_poet
fi

poet-engine -C tcp://${VALIDATOR_IP}:5050 --component tcp://${VALIDATOR_IP}:${VALIDATOR_PORT}

