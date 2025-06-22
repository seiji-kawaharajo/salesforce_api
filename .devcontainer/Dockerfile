ARG DEBIAN_VERSION=bookworm

FROM mcr.microsoft.com/vscode/devcontainers/base:${DEBIAN_VERSION}

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    curl \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER vscode

SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSf https://rye.astral.sh/get | RYE_INSTALL_OPTION="--yes" bash
ENV PATH="/home/vscode/.rye/shims:${PATH}"

# uvを有効化
RUN rye config --set-bool behavior.use-uv=true
