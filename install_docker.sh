#!/bin/bash
# Install Docker Engine + Compose on Zorin OS 17.3 / Ubuntu 22.04

set -e

echo "🐳 Installing Docker Engine + Compose"
echo "======================================"
echo ""

# Prerequisites
echo "📦 Installing prerequisites..."
sudo apt update
sudo apt install -y ca-certificates curl gnupg lsb-release

# Add Docker's GPG key
echo "🔑 Adding Docker's GPG key..."
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "📦 Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo "🐳 Installing Docker Engine..."
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Add user to docker group
echo "👤 Adding $USER to docker group..."
sudo usermod -aG docker $USER

echo ""
echo "============================================"
echo "✅ Docker Installed Successfully!"
echo "============================================"
echo ""
echo "⚠️  IMPORTANT: You must log out and back in"
echo "   (or run: newgrp docker)"
echo "   for group permissions to take effect."
echo ""
echo "Verify installation:"
echo "  docker --version"
echo "  docker compose version"
echo "  docker run hello-world"
