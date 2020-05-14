FROM ubuntu:bionic
ARG DEV=no

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
    python3-grpcio \
    python3-grpcio-tools \
    python3-protobuf \
    python3-sawtooth-sdk \
    protobuf-compiler \
    ipython3 \
    python3-pip

RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir $APP/

COPY node/processor $APP/
COPY node/processor/config/* /etc/sawtooth/
COPY protos/py $APP/protos

WORKDIR $APP

RUN if [ $DEV = "yes" ] ; then REQUIREMENTS_FILE="requirements.dev.txt"; else REQUIREMENTS_FILE="requirements.txt"; fi \
    && pip3 install -r ${REQUIREMENTS_FILE}

EXPOSE 4004/tcp
