FROM ubuntu:bionic

ENV APP=/app

RUN set -xe \
 && apt-get update \
 && apt-get install -y \
    gnupg \
    software-properties-common

RUN set -xe \
 && apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 44FC67F19B2466EA \
 && add-apt-repository 'deb http://repo.sawtooth.me/ubuntu/nightly bionic universe' \
 && apt-get update

RUN set -xe \
 && apt-get install -y \
    python3-sawtooth-sdk \
    python3-pip

RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

RUN mkdir $APP/

COPY api/sync $APP/
COPY protos/py $APP/protos

WORKDIR $APP

RUN pip3 install -r requirements.dev.txt

ENV PYTHONPATH=${PYTHONPATH}:${APP}
