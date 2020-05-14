#!/usr/bin/env bash
source utils.sh


generate_keys () {
    sawadm keygen --force
    sawtooth keygen my_key
    mkdir -p /poet-shared/validator || true
    cp -a /etc/sawtooth/keys /poet-shared/validator/
}

get_poet_batch () {
    while [[ ! -f /poet-shared/poet-enclave-measurement ]]; do sleep 1; done
    while [[ ! -f /poet-shared/poet-enclave-basename ]]; do sleep 1; done
    while [[ ! -f /poet-shared/poet.batch ]]; do sleep 1; done
    cp /poet-shared/poet.batch /
}

build_network_genesis () {
    sawset genesis \
      -k /etc/sawtooth/keys/validator.priv \
      -o config-genesis.batch

    sawset proposal create \
      -k /etc/sawtooth/keys/validator.priv \
      sawtooth.consensus.algorithm.name=PoET \
      sawtooth.consensus.algorithm.version=0.1 \
      sawtooth.poet.report_public_key_pem="$(cat /poet-shared/simulator_rk_pub.pem)" \
      sawtooth.poet.valid_enclave_measurements=$(cat /poet-shared/poet-enclave-measurement) \
      sawtooth.poet.valid_enclave_basenames=$(cat /poet-shared/poet-enclave-basename) \
      -o config.batch

    sawset proposal create \
      -k /etc/sawtooth/keys/validator.priv \
         sawtooth.poet.target_wait_time=5 \
         sawtooth.poet.initial_wait_time=25 \
         sawtooth.publisher.max_batches_per_block=100 \
      -o poet-settings.batch

    sawadm genesis \
      config-genesis.batch config.batch poet.batch poet-settings.batch
}

run () {
    _get_peers_ips () {
        IFS=', ' read -r -a PEERS_LIST <<< "$1"
        OUTPUT=""
        for i in "${PEERS_LIST[@]}"; do
            PEER=$( echo $i | awk -F[/:] '{print $4}' )
            PORT=$( echo $i | awk -F[/:] '{print $5}' )
            PEER_IP=$(get_ip ${PEER})
            OUTPUT=${OUTPUT},tcp://${PEER}:${PORT}
        done

        echo ${OUTPUT:1}
    }

    _get_peers_arg () {
        if [[ ! -z "${PEERS}" ]]; then
            PEERS_IPS=$(_get_peers_ips ${PEERS})
            echo "--peers ${PEERS_IPS}"
        fi
        echo ""
    }

    PEERS_ARG=$(_get_peers_arg)

    # use external IP in case of node per server architecture
    VALIDATOR_IP=${SERVER_IP:-${VALIDATOR_ALIAS}}

    sawtooth-validator -vv \
      --bind network:tcp://eth0:8800 \
      --bind component:tcp://eth0:4004 \
      --bind consensus:tcp://eth0:5050 \
      --endpoint tcp://${VALIDATOR_IP}:${VALIDATOR_PORT} \
      ${PEERS_ARG} \
      --network-auth trust
}

# generate if not exists/first start
# https://github.com/hyperledger/sawtooth-supply-chain/blob/master/docker/compose/supply-chain-default.yaml#L108
if [ ! -f /etc/sawtooth/keys/validator.priv ]; then
    generate_keys

    if [[ -z "${PEERS}" ]]; then
        # If no peers defined, consider is first node which create network.
        get_poet_batch
        build_network_genesis
    fi
fi;

run

