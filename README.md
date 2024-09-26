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
          "*.site.test" \
   && chmod 644 ~/.anydev/certs/*
   ```
6. Configure resolver:
   ```bash
   sudo mkdir -p /etc/resolver && \
   echo "nameserver 127.0.0.1\nport 53" | sudo tee /etc/resolver/site.test
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

## FAQ & Troubleshooting

### Q. Who are my *.site.test domains failing to resolve?
A. Chances are, another resolver is intercepting your requests before they make it to the one we created for AnyDev. Some ISP-issued routers may intercept and serve all requests, even reserved ones like `.test`. To confirm this, use `scutil --dns` to check the resolver order and `dig site.test` to see which server is handling it (it's probably the first one). You may need to manually change your system settings (or network device) to prioritize 127.0.0.1.

### Q. I'm getting and error about port 53 already being in use.
A. First, find out what might already be using it with: `sudo lsof -i :53`
