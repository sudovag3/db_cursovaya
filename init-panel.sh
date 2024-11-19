#!/bin/bash

# Обновление и установка необходимых пакетов
apt update && apt upgrade -y && \
apt install curl fail2ban git bash openssl nano -y && \
systemctl start fail2ban && systemctl enable fail2ban

# Установка Docker
curl -fsSL https://get.docker.com | bash && \
systemctl start docker && systemctl enable docker

# Установка Docker Compose
curl -L "https://github.com/docker/compose/releases/download/$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '\"' -f 4)/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
chmod +x /usr/local/bin/docker-compose

# Клонирование репозитория
git clone https://github.com/MHSanaei/3x-ui.git && \
cd 3x-ui

# Запуск docker-compose
docker compose up -d

# Создание сертификатов
openssl req -x509 -newkey rsa:4096 -nodes -sha256 -keyout private.key -out public.key -days 3650 -subj "/CN=APP"

# Копирование ключей в контейнер
docker cp private.key 3x-ui:private.key
docker cp public.key 3x-ui:public.key

# Получение IP сервера
IP=$(curl -s http://checkip.amazonaws.com)

# Вывод информации
echo "Your panel is running! Check http://$IP:2053/"
