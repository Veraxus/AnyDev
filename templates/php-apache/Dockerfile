# Dockerfile for WordPress
FROM php:8.2-apache

# Install necessary utilities and dependencies
RUN apt-get update \
    && apt-get install -y \
        curl \
        git \
        jq \
        libfreetype6-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        libzip-dev \
        libonig-dev \
        libxml2-dev \
        unzip \
        zip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install -j$(nproc) gd \
    && docker-php-ext-install -j$(nproc) \
        mysqli \
        pdo \
        pdo_mysql  \
        zip  \
        mbstring  \
        exif  \
        pcntl  \
        bcmath  \
        xml  \
        soap \
    && pecl install xdebug \
    && docker-php-ext-enable xdebug \
    && a2enmod env \
    && a2enmod rewrite \
    && curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer

# Set the working directory
WORKDIR /var/www/html

# Set ownership and permissions
RUN chown -R www-data:www-data /var/www/html

# Used by Traefik (SSL terminates at Traefik)
EXPOSE 80