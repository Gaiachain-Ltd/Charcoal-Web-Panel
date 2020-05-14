#!/usr/bin/env bash
source /utils.sh

API_IP=$(get_ip ${API_HOST})

cp -n env.example .env
pip3 install -r requirements/base.txt
python3 manage.py migrate
NODE_API=http://${API_IP}:${API_PORT} POSTGIS_HOST=${POSTGIS_HOST} python3 manage.py runserver 0.0.0.0:8000