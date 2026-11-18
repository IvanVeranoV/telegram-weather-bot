# 🌦️ Telegram Weather Bot

<p align="center">
  <strong>A weather assistant right inside Telegram.</strong><br>
  Search locations, retrieve weather forecasts and get optional AI-powered insights.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white" alt="Python 3.13">
  <img src="https://img.shields.io/badge/Telegram-Bot-26A5E4?logo=telegram&logoColor=white" alt="Telegram Bot">
  <img src="https://img.shields.io/badge/Gemini-Optional_AI-8E75B2?logo=google" alt="Gemini AI">
  <img src="https://img.shields.io/badge/Tests-93%2F93%20passing-success" alt="93 tests passing">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="MIT License">
</p>

---

## ✨ Features

| Feature | Description |
| :--- | :--- |
| 📍 **Location Search** | Find cities and locations using Nominatim and OpenStreetMap. |
| 🌤️ **Weather Forecasts** | Retrieve weather information through Open-Meteo. |
| 🕒 **24-Hour Forecast** | Get a detailed forecast for the upcoming 24 hours. |
| 🤖 **AI Weather Analysis** | Receive an optional interpretation and practical recommendations powered by Google Gemini. |
| ⚡ **Asynchronous Architecture** | Handle external HTTP requests asynchronously. |
| 🛡️ **Error Handling** | Graceful handling of provider errors and AI timeouts. |
| 🔐 **Secret Redaction** | Redact configured credentials from application logs. |

Gemini is optional: the bot continues to provide weather forecasts even when AI analysis is unavailable or not configured.

## 🧰 Tech Stack

- **Python 3.13** – Core programming language.
- **python-telegram-bot** – Telegram Bot API integration.
- **HTTPX** – Asynchronous HTTP client.
- **Nominatim / OpenStreetMap** – Geocoding and location search.
- **Open-Meteo** – Weather forecast data.
- **Google Gen AI SDK** – Optional AI-powered analysis.
- **python-dotenv** – Environment variable management.
- **PyCountry** – Country code validation.
- **pytest** – Automated testing.

## 🏗️ Project Structure

```text
telegram-weather-bot/
├── src/
│   ├── ai/
│   │   ├── providers/
│   │   └── services/
│   ├── config/
│   ├── geocoding/
│   │   ├── models/
│   │   └── providers/
│   ├── telegram_bot/
│   ├── weather/
│   │   ├── models/
│   │   └── providers/
│   └── main.py
├── tests/
│   ├── ai/
│   ├── config/
│   ├── geocoding/
│   │   ├── models/
│   │   └── providers/
│   ├── telegram_bot/
│   └── weather/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── requirements-dev.txt
```

## 🚀 Getting Started

### Requirements

- Python 3.13
- A Telegram bot token from [BotFather](https://t.me/BotFather).

Nominatim and Open-Meteo do not require API keys. Gemini analysis is optional and requires a key from [Google AI Studio](https://aistudio.google.com/apikey).

### 1. Clone the repository

```bash
git clone https://github.com/IvanVeranoV/telegram-weather-bot.git
cd telegram-weather-bot
```

### 2. Create a virtual environment

**Windows (PowerShell)**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create a Telegram bot using [BotFather](https://t.me/BotFather), then copy the example environment file.

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Edit `.env` and configure your credentials:

```dotenv
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
APP_ENV=development

# Optional: enables AI weather analysis
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Gemini is optional. Without `GEMINI_API_KEY`, the bot works normally and provides weather forecasts without AI analysis.

The model can be changed using `GEMINI_MODEL`.

> 🔐 Never commit your `.env` file or expose your credentials publicly.

## 💬 Usage

Start the bot from the project root:

```bash
python -m src.main
```

Open Telegram and interact with your bot using these commands:

| Command | Description |
| :--- | :--- |
| `/start` | Start interacting with the bot. |
| `/search` | Search for a city or location. |
| `/search <city>` | Search directly for a specific city. |
| `/cancel` | Cancel a pending location search. |
| `/forecast` | Retrieve the detailed 24-hour forecast and optional AI analysis. |

The initial weather summary displays the upcoming forecast periods.

The `/forecast` command provides a detailed 24-hour forecast. When Gemini is enabled, the bot also sends a separate message containing an interpretation and practical recommendations based on the normalized forecast data.

If Gemini is unavailable or takes too long to respond, the weather forecast is still delivered.

## 🧪 Testing

Run the automated test suite from the project root:

```bash
python -m pytest
```

The latest verified test run completed successfully: **93/93 tests passing**.

The project includes automated tests covering configuration, geocoding, weather providers, Telegram interactions and AI integration.

## 🔌 Data Providers & Attribution

This project relies on the following external services:

- [Open-Meteo](https://open-meteo.com/) – Weather forecast data.
- [Nominatim](https://nominatim.org/) – Geocoding and location search.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) – Geographical data.
- [Google Gemini](https://ai.google.dev/gemini-api/docs) – Optional AI weather analysis.

Please respect the usage policies and attribution requirements of these services.

## 🔐 Security

- Credentials are managed through environment variables.
- `.env` is excluded from version control.
- Configured secrets are redacted from application logs.
- Gemini API credentials are optional and must remain private.
- Each user must configure their own Telegram bot token.

## 📌 Project Status

**MVP completed — currently on hold.**

The initial implementation is complete, with location search, weather retrieval, Telegram integration and optional AI-powered weather analysis.

The project has reached its current MVP milestone, with **93 automated tests passing**. Further development may resume in the future.

## 👨‍💻 Author

**Iván Verano**

- GitHub: [@IvanVeranoV](https://github.com/IvanVeranoV)

## 📄 License

This project is licensed under the [MIT License](LICENSE).
