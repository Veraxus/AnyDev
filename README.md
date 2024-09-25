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
2. Install Docker
   ```bash
   brew install --cask docker
   ```
3. Install Mkcert & NSS:  
   ```bash
   brew install mkcert nss
   ```

## Starting

1. Make a copy of `.env.example` and name it `.env`
2. Update the values in `.env`
3. Starting the services
   ```bash
   docker compose --profile lamp up -d
   ```