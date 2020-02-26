FROM ubuntu:18.04

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y \
	python3-pip \
	curl \
	git

RUN pip3 install --upgrade pip
RUN set -ex && \
    pip install https://github.com/chris-belcher/electrum-personal-server/archive/eps-v0.2.0.tar.gz#egg=electrum-personal-server

# Copy the entrypoint script.
COPY "docker/electrum/start-electrum.sh" .
COPY "docker/electrum/config.ini.sh" .
RUN chmod +x start-electrum.sh
