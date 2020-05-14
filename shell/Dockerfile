FROM hyperledger/sawtooth-shell:1.1

RUN set -xe \
 && apt-get update \
 && apt-get install -y \
    python3-setuptools \
    telnet\
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

COPY . /opt/
WORKDIR /opt/
RUN python3 setup.py install
