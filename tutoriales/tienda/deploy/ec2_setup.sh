#!/usr/bin/env bash
# Tutorial 04 - Paso 4.3/4.4: preparar la instancia EC2 (Amazon Linux 2023) y desplegar.
# Uso en EC2 Instance Connect:
#   curl -fsSL https://raw.githubusercontent.com/NicoRDJ/ing-software-EAFIT/main/tutoriales/tienda/deploy/ec2_setup.sh | bash
set -e
REPO_URL="${REPO_URL:-https://github.com/NicoRDJ/ing-software-EAFIT.git}"
DIR="$HOME/ing-software-EAFIT"

# Actualizar el sistema e instalar Git y Docker
sudo dnf update -y
sudo dnf install -y git docker
sudo systemctl enable --now docker
sudo usermod -a -G docker ec2-user

# Plugin docker compose v2 (Amazon Linux 2023 no lo trae por defecto)
sudo mkdir -p /usr/local/lib/docker/cli-plugins
sudo curl -fsSL "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-$(uname -m)" \
  -o /usr/local/lib/docker/cli-plugins/docker-compose
sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Clonar (o actualizar) el repositorio y levantar la arquitectura
if [ -d "$DIR/.git" ]; then git -C "$DIR" pull origin main; else git clone "$REPO_URL" "$DIR"; fi
cd "$DIR/tutoriales/tienda"
sudo docker compose up -d --build
sudo docker ps

echo ""
echo "Listo. IP publica de esta instancia:"
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4; echo
