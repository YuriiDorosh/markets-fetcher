#!/bin/bash

# Оновлення пакетів
sudo apt update

# Відкриття портів
sudo apt install ufw
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable

# IP
sudo apt install curl
curl ifconfig.me > ip.txt

# Встановлення необхідних пакетів
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Додавання ключа GPG Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Додавання репозиторію Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Оновлення списку пакетів
sudo apt update

# Встановлення Docker CE
sudo apt install -y docker-ce

# Перевірка статусу Docker
sudo systemctl status docker

# Встановлення Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Встановлення прав виконання
sudo chmod +x /usr/local/bin/docker-compose

# Перевірка версії Docker Compose
docker-compose --version

# Підняття контейнера з використанням docker-compose
docker-compose up --build
