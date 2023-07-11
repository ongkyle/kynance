ARG BUILD_PLATFORM

FROM --platform=$BUILD_PLATFORM arm32v7/ubuntu:focal

RUN \
    apt-get update && \
    apt-get install -y \
    software-properties-common  && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y \
    curl \
    libssl-dev \
    pkg-config \
    libxslt-dev \
    libatlas-base-dev \
    python3.9 \
    python3.9-dev \
    python3-pip && \
    rm -rf /var/lib/apt/lists/* && \
    python3.9 -m pip install --upgrade pip && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

ENV PATH="/root/.cargo/bin:${PATH}"

COPY requirements-arm32v7l.txt requirements.txt

RUN \
    --mount=type=cache,target=/var/cache/pip \
     python3.9 -m pip install --no-cache-dir \
    --extra-index-url=https://www.piwheels.org/simple \
    -r requirements.txt