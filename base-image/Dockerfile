ARG BASE_IMAGE=python
ARG BASE_IMAGE_TAG=3.11.9-slim-bookworm
ARG POETRY_VERSION=2.1.1
FROM ${BASE_IMAGE}:${BASE_IMAGE_TAG}

# Update and install necessary packages
RUN apt-get update && \
    apt-get install -y rsync pkg-config libxml2-dev libxmlsec1-dev \
        libxmlsec1-openssl curl git libc-bin locales libcurl3-gnutls \
        build-essential python3-dev libpq-dev libpq-dev

# Fix vulnerabilities with old packages
RUN apt-get upgrade -y libaom3 git openexr zlib1g-dev

# Install pipx
RUN python3 -m pip install pipx && pipx ensurepath

# Set $POETRY_HOME env var for child images to reference and add it to the $PATH
ENV POETRY_HOME='/root/.local'
ENV PATH="${POETRY_HOME}/bin:$PATH"

# Install Poetry
RUN pipx install poetry==2.1.1

# Install Poetry's bundle plugin to install cleanly in a virtual environment
RUN pipx inject poetry poetry-plugin-bundle

# Make sure poetry is installed
RUN poetry --version
