FROM ubuntu:bionic

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

ARG DEV=no

ENV APP=/poc-api

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
    python3-pip

RUN set -xe \
  && apt-get update \
  && apt-get install -y gdal-bin python-gdal python3-gdal

RUN apt-get clean \
 && rm -rf /var/lib/apt/lists/*

ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# create root directory for our project in the container
RUN mkdir $APP/

# Copy the current directory contents into the container at /poc-api
COPY api/poc-api $APP/

# Set the working directory to /poc-api
WORKDIR $APP

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements/base.txt

ENV PYTHONPATH=${PYTHONPATH}:${APP}
