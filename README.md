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
* Minikube - Kubernetes service
* Minikube Metrics Server - Auto-scaling for production-similar local architecture
* Traefik - Application proxy for routing, SSL termination, etc
* Helm - Kubernetes dependency management

## Setup

### Mac OS
Note: Currently only MacOS is supported. Additional platforms coming soon.

1. Install [Homebrew](https://brew.sh/):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
2. Install Minikube, Mkcert, NSS, and Helm:  
   ```bash
   brew install minikube mkcert nss helm
   ```
3. Start Minikube:
   ```bash
   minikube start --nodes=3 --cpus=4 --memory=8192 --driver=hyperkit
   ```
4. Enable ingress & metric to emulate prod features:
   ```bash
   minikube addons enable metrics-server
   ```
5. Install CA certs on host:
   ```bash
   mkcert -install
   ```
6. Create certs for local *.site.local TLD:
   ```bash
   mkcert -key-file "$(mkcert -CAROOT)/_wildcard.site.local-key.pem" -cert-file "$(mkcert -CAROOT)/_wildcard.site.local.pem"  "*.site.local"
   ```
7. Add CA cert to k8s:
   ```bash
   kubectl create configmap mkcert-ca --from-file="$(mkcert -CAROOT)/rootCA.pem"
   ```
8. Add k8s wildcard certificates to k8s secrets:
   ```bash
   kubectl create secret tls site-local-tls --key="$(mkcert -CAROOT)/_wildcard.site.local-key.pem" --cert="$(mkcert -CAROOT)/_wildcard.site.local.pem"
   ```
9. Add bitnami repo...
   ```bash
   helm repo add bitnami https://charts.bitnami.com/bitnami && \
   helm repo update
   ```
10. Install the Helm chart for Traefik:
   ```bash
   helm repo add traefik https://helm.traefik.io/traefik && \
   helm repo update
   ```
11. Install Traefik {{Using defaults?}}:
   ```bash
   helm install traefik traefik/traefik --namespace anydev
   ```

## Notes
Check on pods
```bash
kubectl get pods
```

Add shared service: MySQL
```bash
helm install mysql bitnami/mysql --namespace anydev -f ./kubes/mysql-values.yaml
```

Add shared service: MongoDB
```bash
helm install mongodb bitnami/mongodb --namespace anydev -f ./kubes/mongodb-values.yaml
```

TODO: Add shared service: Selenium
```bash
kubectl apply -f ./kubes/selenium-grid.yaml
```
TODO: Add shared service: Memcached
```bash
helm install memcached bitnami/memcached --namespace anydev -f ./kubes/memcached-values.yaml
```

TODO: Add shared service: Redis
```bash
helm install redis bitnami/redis --namespace anydev -f ./kubes/redis-values.yaml
```

TODO: Add an Apache-PHP web server for pawstime.site.local
TODO: Add an Apache-PHP web server for laravel.site.local
TODO: Add a RoR web server for rails.site.local