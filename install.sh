#!/bin/bash

# Multi-Platform Bot Installation Script
# Instaluje i konfiguruje boty na serwerze Linux

set -e

echo "🚀 Installing Multi-Platform Bot System..."

# Sprawdź czy jesteś root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Uruchom jako root: sudo $0"
    exit 1
fi

# Utwórz użytkownika botuser
if ! id "botuser" &>/dev/null; then
    echo "👤 Tworzenie użytkownika botuser..."
    useradd -m -s /bin/bash botuser
fi

# Utwórz katalog aplikacji
echo "📁 Tworzenie katalogów..."
mkdir -p /opt/bots
chown botuser:botuser /opt/bots

# Skopiuj pliki aplikacji
echo "📋 Kopiowanie plików..."
cp -r . /opt/bots/
chown -R botuser:botuser /opt/bots

# Zainstaluj zależności Python
echo "📦 Instalowanie zależności Python..."
apt-get update
apt-get install -y python3 python3-pip python3-venv

# Utwórz środowisko wirtualne
echo "🐍 Tworzenie środowiska wirtualnego..."
sudo -u botuser python3 -m venv /opt/bots/venv
sudo -u botuser /opt/bots/venv/bin/pip install -r /opt/bots/requirements.txt

# Skopiuj service file
echo "⚙️ Konfiguracja systemd..."
cp multi-platform-bot.service /etc/systemd/system/
systemctl daemon-reload

# Włącz automatyczne uruchamianie
systemctl enable multi-platform-bot.service

echo "✅ Instalacja zakończona!"
echo ""
echo "📝 Następne kroki:"
echo "1. Skonfiguruj plik .env w /opt/bots/.env"
echo "2. Uruchom serwis: sudo systemctl start multi-platform-bot"
echo "3. Sprawdź status: sudo systemctl status multi-platform-bot"
echo "4. Zobacz logi: sudo journalctl -u multi-platform-bot -f"
