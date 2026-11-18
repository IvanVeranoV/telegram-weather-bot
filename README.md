# Telegram Weather Bot

A Telegram bot built with Python that provides weather forecasts for user-selected locations. It uses Open-Meteo for weather data and Nominatim for geographical search, with optional AI-powered weather analysis through Gemini.

## Features

- Search for cities and locations using Nominatim.
- Select the desired location when multiple search results are available.
- Retrieve weather forecasts from Open-Meteo.
- Display a concise weather summary for the upcoming hours.
- Request a detailed 24-hour forecast.
- Add an optional AI interpretation of the 24-hour forecast using Gemini.
- Handle asynchronous HTTP requests.
- Validate and normalize external provider responses.

## Tech Stack

- **Python 3.13**
- **python-telegram-bot** – Telegram Bot API integration.
- **HTTPX** – Asynchronous HTTP client.
- **python-dotenv** – Environment variable management.
- **PyCountry** – Country code validation.
- **Nominatim / OpenStreetMap** – Geocoding and location search.
- **Open-Meteo** – Weather forecast data.
- **Google Gen AI SDK** – Optional AI-powered weather analysis.
- **pytest** – Automated testing.

## Project Structure

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

## Requirements

- Python 3.13.
- A Telegram bot token obtained through [BotFather](https://t.me/BotFather).

The Nominatim and Open-Meteo services do not require API keys. Gemini analysis is optional and requires a Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey).

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/IvanVeranoV/telegram-weather-bot.git
cd telegram-weather-bot
```

### 2. Create a virtual environment

**Windows (PowerShell):**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

Install the development dependencies, including the runtime requirements:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Configure environment variables

Create your own Telegram bot using [BotFather](https://t.me/BotFather) and obtain its token.

Copy the example environment file:

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Open `.env` and provide your Telegram token. To enable AI analysis in `/forecast`, also provide a Gemini API key:

```dotenv
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.8-flash
```

Gemini is optional. If `GEMINI_API_KEY` is not configured, the bot continues to provide weather forecasts without AI analysis. The model can be changed through `GEMINI_MODEL`.

Never commit your `.env` file or share your credentials publicly.

## Usage

Start the bot from the project root:

```bash
python -m src.main
```

Open your bot in Telegram and use the following commands:

| Command | Description |
| :--- | :--- |
| `/start` | Start interacting with the bot. |
| `/search` | Search for a city or location. |
| `/search <city>` | Search directly for a specific city. |
| `/cancel` | Cancel a pending location search. |
| `/forecast` | Retrieve the 24-hour forecast and, when configured, an AI analysis. |

The initial weather summary displays the upcoming forecast periods. The `/forecast` command provides the detailed 24-hour forecast. When Gemini is enabled, a separate message adds a concise interpretation and practical recommendations based only on the normalized forecast data.

## Running Tests

Run the automated test suite from the project root:

```bash
python -m pytest
```

## Data Providers and Attribution

This project uses the following external services:

- [Open-Meteo](https://open-meteo.com/) for weather forecast data.
- [Nominatim](https://nominatim.org/) for geocoding and location search.
- [OpenStreetMap](https://www.openstreetmap.org/copyright) for geographical data.
- [Google Gemini](https://ai.google.dev/gemini-api/docs) for optional AI weather analysis.

Please respect the usage policies and attribution requirements of these services when using or extending this project.

## Project Status

This project is under active development. The current implementation focuses on location search, weather retrieval, Telegram integration and optional AI-powered weather analysis.

## Security

- Credentials are managed through environment variables.
- The `.env` file must remain local and must never be committed.
- Each user must provide their own Telegram bot token.
- The Gemini API key is optional and must also remain private.

## Author

### Iván Verano

GitHub: [@IvanVeranoV](https://github.com/IvanVeranoV)

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
