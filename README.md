# AnyDev
Create portable, containerized local development environments for any stack.

## Project Goals
* It must be extremely easy to get up and running, even for novices.
* It must support multiple applications simultaneously, accessible via friendly host names.
* It must be architecturally similar to common, simple production configurations.
* It must be usable on most common platforms (MacOS, Windows, & various Linux distros)
* It must be easily configurable to support various common stacks.
* It must be extensible to easily add new technologies or stacks.

## Architecture Considerations
* mkcert + nss - Self-signed certificates for local HTTPS
* Traefik - Application proxy for routing, SSL termination, etc

## Setup
Note: Currently only MacOS is supported. Additional platforms coming soon.

### Configure Host Dependencies

1. Install [Homebrew](https://brew.sh/):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Docker:  
   ```bash
   brew install --cask docker
   ```
3. Install mkcert & nss:  
   ```bash
   brew install mkcert nss
   ```
4. Generate CA certificates:  
   ```bash
      export CAROOT=~/.anydev/certs/ mkcert --install && \
   ```
5. Generate wildcard certificates for local domains:  
   ```bash
      mkcert -key-file "~/.anydev/certs/_wildcard.site.local-key.pem" -cert-file "~/.anydev/certs/_wildcard.site.local.pem"  "*.site.local"
   ```

## Starting Shared Services

1. Create a .env file...
   ```bash
   cp .env.example .env
   ```
2. Starting the services (LAMP stack)...
   ```bash
   docker compose --profile lamp up -d
   ```

## Starting An Application

1. Make a copy of a template directory or create your own.