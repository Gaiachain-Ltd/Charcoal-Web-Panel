#!/usr/bin/env bash

get_ip () {
    echo $(getent hosts $1 | cut -d' '  -f1)
}

