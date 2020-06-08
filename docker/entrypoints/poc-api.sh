#!/usr/bin/env bash
source /utils.sh

API_IP=$(get_ip ${API_HOST})

cp -n env.example .env
pip3 install -r requirements/base.txt
while !</dev/tcp/${POSTGIS_HOST}/5432; do sleep 1; done;
python3 manage.py migrate
NODE_API=http://${API_IP}:${API_PORT} POSTGIS_HOST=${POSTGIS_HOST} SERVER_PORT=${SERVER_PORT} python3 manage.py runserver 0.0.0.0:8000