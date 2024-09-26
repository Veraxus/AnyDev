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
4. Generate CA certificates & move to anydev:  
   ```bash
   mkcert --install && \
   mkdir -p ~/.anydev/certs/ && \
   cp "$(mkcert -CAROOT)"/* ~/.anydev/certs/
   ```
5. Generate wildcard certificates for local domains:  
   ```bash
   mkcert -key-file ~/.anydev/certs/_wildcard.site.test-key.pem \
          -cert-file ~/.anydev/certs/_wildcard.site.test.pem  \
          "*.site.test"
   ```
6. Configure resolver:
   ```bash
   sudo mkdir -p /etc/resolver && \
   echo "nameserver 127.0.0.1
   port 53535" | sudo tee /etc/resolver/site.test
   ```
7. Start the support services:
   ```bash
   docker compose up -d
   ```
   Also note that you can use profiles to start multiple specific services or stacks:
   ```bash
   docker compose \
      --profile mysql \
      --profile redis \
      up -d
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

1. Make a copy of your preferred template directory anywhere on your system.
2. Create a `.env` using `.env.example` as a guide.
3. Run `docker compose up -d`
4. Start building your project to the ./src directory!

## FAQ

### Q. Why does dnsmasq use port 5353
**A.** DNS normally uses port 53, but on some machines there can be a conflict (or a Docker bug) that can cause problems, and troubleshooting this can require serious technical chops. Instead, AnyDev uses 5353 to avoid conflicts and ensure setup remains easy.

