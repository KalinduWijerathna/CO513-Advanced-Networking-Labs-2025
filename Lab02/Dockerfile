FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3 \
    iperf3 \
    iproute2 \
    net-tools \
    iputils-ping \
    bash \
    sudo \
    build-essential \
    libssl-dev \
    git \
    unzip \
    && apt-get clean

# Install wrk from source
RUN git clone https://github.com/wg/wrk.git /opt/wrk && \
    make -C /opt/wrk && \
    ln -s /opt/wrk/wrk /usr/local/bin/wrk

