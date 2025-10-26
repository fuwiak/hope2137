# 🚀 Multi-Platform Bot Deployment Guide

## 📋 Przegląd

System uruchamia **oba boty jednocześnie**:
- 🤖 **Telegram Bot** - główny bot
- 📱 **WhatsApp Bot** - dodatkowy bot (opcjonalny)

## 🎯 Sposoby Deploymentu

### 1. 🐳 Railway (Zalecane)

**Najłatwiejszy sposób - automatyczny deployment:**

```bash
# 1. Commit i push zmian
git add .
git commit -m "Add multi-platform bot support"
git push origin main

# 2. Railway automatycznie zbuduje i uruchomi oba boty
```

**Konfiguracja Railway:**
- ✅ `railway.json` - używa `run_bots.py`
- ✅ `Dockerfile` - uruchamia oba boty
- ✅ Automatyczne restartowanie przy błędach

### 2. 🖥️ Lokalny Serwer Linux

**Instalacja na własnym serwerze:**

```bash
# 1. Sklonuj repozytorium
git clone <your-repo-url>
cd <repo-directory>

# 2. Uruchom instalator (jako root)
sudo ./install.sh

# 3. Skonfiguruj zmienne środowiskowe
sudo nano /opt/bots/.env

# 4. Uruchom serwis
sudo systemctl start multi-platform-bot
sudo systemctl enable multi-platform-bot

# 5. Sprawdź status
sudo systemctl status multi-platform-bot
```

**Zarządzanie serwisem:**
```bash
# Uruchom
sudo systemctl start multi-platform-bot

# Zatrzymaj
sudo systemctl stop multi-platform-bot

# Restart
sudo systemctl restart multi-platform-bot

# Zobacz logi
sudo journalctl -u multi-platform-bot -f
```

### 3. 💻 Lokalny Development

**Uruchomienie na własnym komputerze:**

```bash
# Szybki start
./start_bots.sh

# Lub ręcznie
python3 run_bots.py
```

## ⚙️ Konfiguracja

### Wymagane zmienne (.env):

```env
# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_token

# YClients API
YCLIENTS_PARTNER_TOKEN=your_partner_token
YCLIENTS_USER_TOKEN=your_user_token

# Groq AI
GROQ_API_KEY=your_groq_key

# WhatsApp Bot (opcjonalne)
GREEN_API_ID=your_green_api_id
GREEN_API_TOKEN=your_green_api_token
```

### Logika działania:

1. **Telegram Bot** - zawsze uruchamiany
2. **WhatsApp Bot** - uruchamiany tylko jeśli są dostępne `GREEN_API_ID` i `GREEN_API_TOKEN`
3. **Monitoring** - system sprawdza czy oba boty działają
4. **Restart** - automatyczne restartowanie przy błędach

## 🔍 Monitoring i Debugging

### Railway:
- Logi dostępne w Railway Dashboard
- Automatyczne restartowanie przy błędach

### Serwer Linux:
```bash
# Status serwisu
sudo systemctl status multi-platform-bot

# Logi w czasie rzeczywistym
sudo journalctl -u multi-platform-bot -f

# Logi z ostatnich 100 linii
sudo journalctl -u multi-platform-bot -n 100
```

### Lokalny:
```bash
# Logi w konsoli
python3 run_bots.py

# Sprawdź procesy
ps aux | grep python
```

## 🚨 Rozwiązywanie problemów

### Bot nie uruchamia się:
1. Sprawdź zmienne środowiskowe
2. Sprawdź logi błędów
3. Sprawdź czy porty są wolne

### WhatsApp Bot nie działa:
1. Sprawdź `GREEN_API_ID` i `GREEN_API_TOKEN`
2. Sprawdź webhook w Green API cabinet
3. Sprawdź czy numer telefonu jest autoryzowany

### Telegram Bot nie działa:
1. Sprawdź `TELEGRAM_BOT_TOKEN`
2. Sprawdź połączenie internetowe
3. Sprawdź logi błędów

## 📊 Architektura

```
run_bots.py
├── Telegram Bot Thread
│   └── app.py
└── WhatsApp Bot Thread (opcjonalny)
    └── whatsapp_bot.py

Wspólne zasoby:
├── YClients API
├── Groq AI
└── User Memory
```

## ✅ Gotowe do użycia!

Po deploymentzie oba boty będą działać jednocześnie i obsługiwać klientów na obu platformach.
