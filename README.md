# AnyDev
Create portable, containerized local development environments for any stack.

## Features & Architecture
AnyDev allows you to run web applications on your own computer using HTTPS and unique domains, so you can access any number of projects with local-only domains like https://*.site.test

To accomplish this, we use [dnsmasq](https://en.wikipedia.org/wiki/Dnsmasq) for host + internal DNS and [traefik](https://doc.traefik.io/traefik/) for Docker-based routing. The host machine needs a few dependencies as well, to ensure HTTPS works correctly from your web browser: this includes [mkcert](https://github.com/FiloSottile/mkcert) and some minimal host DNS/resolver configuration.

Additionally, AnyDev can easily and automatically run shared services (like Mongo, MySQL, Redis, etc), with everything pre-configured for you.

AnyDev also includes Docker-based "application templates" for a wide variety of languages and stacks, so you have an easy single-command starting point for new projects, as well as seamlessly running multiple projects simultaneously, using both shared AnyDev services or application-specific ones.

[MailPit](https://mailpit.axllent.org/docs/configuration/runtime-options/) is also included for local email testing, with a web UI available at https://mailpit.site.test.

Note: The goal is for AnyDev to work on all major platforms: Mac, Windows, and Linux. Currently, Windows is not yet supported due to its unique DNS and configuration limitations. If you would like to contribute to enabling Windows support, PRs are welcome!

## Usage
AnyDev is in an alpha state and is not currently ready for prime-time. Currently, this is very MacOS-centric, though
Windows and Linux support is planned. To get up and running right away, see the [contributing](#contributing) section
below.

## Contributing

### Setup
#### 1. Prep the Project
To get started:
1. [Install Poetry](https://python-poetry.org/docs/#installation)
2. Clone this repo!
3. From your terminal, run the following in the project directory...
   ```bash
   poetry install
   ```

#### 2. Configure Host Dependencies (MacOS)

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

#### 3. Start Shared Services

1. Create a .env file...
   ```bash
   cp .env.example .env
   ```
2. Start the support services:
   ```bash
   docker compose up -d
   ```
   Also note that you can use profiles to start multiple specific services:
   ```bash
   docker compose \
      --profile mysql \
      --profile redis \
      up -d
   ```

### 4. Create shortcut
Be sure to create a shortcut in your profile so that you can run AnyDev from anywhere (it's supposed to be context-sensitive, after all)
```bash
# Allow AnyDev to be used from anywhere (e.g. projects)
anydev() {
    poetry --directory ~/path/to/anydev/directory run anydev "$@"
}
# Shorthand shortcut...
ad() {
    anydev "$@"
}
```

#### 5. Ready to go!
Access commands with `anydev ...` or create a convenient alias in your shell profile.

If you need to configure the environment with your IDE, you can get the poetry env path with...
```bash
poetry env info --path
```

### Project Goals
* It must be extremely easy to get up and running, even for novices.
* It must support multiple applications simultaneously, accessible via friendly host names.
* It must be architecturally similar to common, simple production configurations.
* It must be usable on most common platforms (MacOS, Windows, & various Linux distros)
* It must be easily configurable to support various common stacks.
* It must be extensible to easily add new technologies or stacks.

### Architecture Considerations
* mkcert + nss - Self-signed certificates for local HTTPS. Run on host machine.
* Traefik - Application proxy for routing, SSL termination, etc.
* dnsmasq - DNS for AnyDev's *.site.test domain. Use resolver on host to route traffic.

## FAQ & Troubleshooting

### Q. Why are my *.site.test domains failing to resolve?
A. Chances are, another resolver is intercepting your requests before they make it to the one we created for AnyDev. Some ISP-issued routers may intercept and serve all requests, even reserved ones like `.test`. To confirm this, use `scutil --dns` to check the resolver order and `dig site.test` to see which server is handling it (it's probably the first one). You may need to manually change your system settings (or network device) to prioritize 127.0.0.1.

### Q. I'm getting and error about port 53 already being in use.
A. First, find out what might already be using it with: `sudo lsof -i :53`
