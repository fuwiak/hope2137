# 🤖 Multi-Platform Bot System

Bot na Telegram i WhatsApp dla salonu красоты z integracją YClients API.

## 🚀 Funkcje

### Telegram Bot
- ✅ Rezerwacja wizyt
- ✅ Wyświetlanie usług i cen
- ✅ Lista мастеров
- ✅ Zarządzanie записями
- ✅ AI chat

### WhatsApp Bot  
- ✅ Te same funkcje co Telegram
- ✅ Równoległa praca
- ✅ Wspólna baza danych
- ✅ QR code authentication

## 📋 Wymagania

### System
- Python 3.8+
- Node.js 16+
- Docker (opcjonalnie)

### API Keys
- `TELEGRAM_BOT_TOKEN` - Token bota Telegram
- `GROQ_API_KEY` - Klucz API Groq (AI)
- `YCLIENTS_PARTNER_TOKEN` - Token partnera YClients
- `YCLIENTS_USER_TOKEN` - Token użytkownika YClients

## 🛠 Instalacja

### 1. Klonowanie repozytorium
```bash
git clone <repository-url>
cd hope2137
```

### 2. Instalacja Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Instalacja Node.js dependencies
```bash
npm install
```

### 4. Konfiguracja środowiska
```bash
cp .env.example .env
# Edytuj .env i dodaj swoje klucze API
```

## 🚀 Uruchamianie

### Opcja 1: Tylko Telegram Bot
```bash
python app.py
```

### Opcja 2: Tylko WhatsApp Bot
```bash
python whatsapp_bot.py
```

### Opcja 3: Oba boty równolegle
```bash
python multi_bot.py
```

### Opcja 4: Docker Compose
```bash
# Wszystkie boty
docker-compose up multi-bot

# Tylko Telegram
docker-compose up telegram-bot

# Tylko WhatsApp
docker-compose up whatsapp-bot
```

## 📱 Pierwsze uruchomienie WhatsApp

1. Uruchom WhatsApp bot
2. Zeskanuj QR code telefonem
3. Bot będzie połączony z Twoim kontem WhatsApp

## 🔧 Struktura plików

```
├── app.py                 # Telegram bot
├── whatsapp_bot.py        # WhatsApp bot
├── whatsapp_bridge.js     # Node.js bridge
├── multi_bot.py           # Launcher dla obu botów
├── yclients_client.py    # YClients API client
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker configuration
└── Dockerfile            # Multi-stage Docker build
```

## 🎯 Funkcje botów

### Rezerwacja wizyt
- Automatyczne parsowanie wiadomości
- Walidacja dostępności czasu
- Tworzenie rzeczywistych rezerwacji w YClients
- Obsługa konfliktów czasowych

### Wyświetlanie usług
- Prawdziwe ceny z API
- Wszystkie usługi dla każdego мастера
- Paginacja dla długich list
- Brak wymyślanych danych

### AI Chat
- Inteligentne odpowiedzi
- Historia konwersacji
- Parsowanie intencji użytkownika

## 🔒 Bezpieczeństwo

- Walidacja wszystkich danych z API
- Brak hardcoded informacji
- Bezpieczne przechowywanie sesji
- Non-root user w Docker

## 📊 Logowanie

Wszystkie boty logują:
- API calls do YClients
- Odpowiedzi AI
- Błędy i ostrzeżenia
- Statystyki użycia

## 🚀 Deployment

### Railway
```bash
# Użyj multi_bot.py jako entry point
# Railway automatycznie zainstaluje Node.js i Python dependencies
```

### Docker
```bash
docker build -t multi-platform-bot .
docker run -d --env-file .env multi-platform-bot
```

## 🐛 Troubleshooting

### WhatsApp Bot nie działa
1. Sprawdź czy Node.js jest zainstalowany
2. Uruchom `npm install`
3. Sprawdź logi dla błędów QR code

### Telegram Bot nie odpowiada
1. Sprawdź `TELEGRAM_BOT_TOKEN`
2. Sprawdź czy bot jest aktywny w @BotFather

### API błędy
1. Sprawdź YClients credentials
2. Sprawdź logi dla szczegółów błędów

## 📈 Monitoring

Boty logują wszystkie ważne wydarzenia:
- Rezerwacje
- Błędy API
- Użycie AI
- Statystyki użytkowników

## 🤝 Wsparcie

W przypadku problemów:
1. Sprawdź logi
2. Sprawdź konfigurację .env
3. Sprawdź status API YClients
4. Sprawdź połączenie internetowe

## 📝 Licencja

MIT License - możesz używać, modyfikować i dystrybuować.
