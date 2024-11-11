FROM debian:bookworm-slim AS builder

# Install required packages in one RUN command to reduce layers and image size
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get purge -y imagemagick imagemagick-6-common \
    && apt-get install -y --no-install-recommends \
       curl git wget xz-utils vim ca-certificates locales \
       build-essential bzip2 zsh jq openssh-client openssh-server \
       bzip2 unzip sudo libssl-dev pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set shell options for better error handling
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Nix, uv, mcfly, micro-mamba, and Rust in one RUN command to minimize layers
RUN curl -L https://nixos.org/nix/install | sh -s -- --daemon && \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh | sh && \
    curl -L micro.mamba.pm/install.sh | sh && \
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
    wget https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64 -O /usr/bin/yq && \
    chmod +x /usr/bin/yq

# Install Rust-based tools
RUN source $HOME/.cargo/env && cargo install --locked bat jaq

# Set up locales
RUN locale-gen en_US.UTF-8 && \
    echo "export LANG=en_US.UTF-8" >> /etc/profile

# Configure zsh, Nix, and mcfly in .zshrc
RUN echo "source $HOME/.nix-profile/etc/profile.d/nix.sh" >> "$HOME/.zshrc" && \
    echo "experimental-features = nix-command flakes" >> /etc/nix/nix.conf

# Change default shell to zsh
RUN chsh -s /bin/zsh

ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /workspace/todo

RUN apt-get update --fix-missing && apt-get install -y --fix-missing build-essential

# Install specific Python versions with uv
RUN uv python install 3.11 3.12

# Final image shell and entrypoint configuration
SHELL ["/bin/zsh", "-c"]

# Entrypoint to start an interactive shell session
CMD ["zsh"]
