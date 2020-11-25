# Gaiachain

## Running the app locally
### Single node
`SERVER_PORT=8031 PREFIX=node1 docker-compose -p node1 -f docker/base.yaml -f docker/client.yaml up`

Webpanel for a node is available at http://localhost:{SERVER_PORT} (SERVER_PORT=8031 in this case)

### Multiple nodes
Running multiple nodes enables syncronization between blockchain nodes

`PEERS=tcp://node1_validator:8800 SERVER_PORT=8131 PREFIX=node2 docker-compose -p node2 -f docker/base.yaml -f docker/client.yaml up`

Running multiple nodes requires passing **PEERS** variable in order to connect nodes. Every next node requires all previous validator urls to be passed in **PEERS**

`PEERS=tcp://node1_validator:8800,tcp://node2_validator:8800 SERVER_PORT=8231 PREFIX=node3 docker-compose -p node3 -f docker/base.yaml -f docker/client.yaml up`

## Running the app distributed/per server
It is almost the same except that it needs a new variable being passed for every node: **SERVER_IP**

First node:

`SERVER_PORT=8031 SERVER_IP=8.8.8.8 PREFIX=node1 docker-compose -p node1 -f docker/base.yaml -f docker/client.yaml up`

Every next node (*PEERS and SERVER_IP are set accordingly*):

`PEERS=tcp://8.8.8.8:8800 SERVER_IP=9.9.9.9 SERVER_PORT=8031 PREFIX=node2 docker-compose -p node2 -f docker/base.yaml -f docker/client.yaml up`
