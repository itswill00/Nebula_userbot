# Nebula Engine v1.6.0

A high-performance, modular Telegram Userbot built on the Hydrogram framework. Nebula Engine is designed for efficiency, stability, and extensibility, providing a seamless automation experience with a focus on core performance.

## Key Features

- **Hydrogram Core**: Leveraging the latest MTProto implementation for speed and security.
- **Asynchronous Architecture**: Fully non-blocking operations using `asyncio` and `uvloop`.
- **Modular Plugin System**: Easily extendable with a structured plugin architecture.
- **Integrated Assistant Bot**: Built-in support for an inline assistant bot for help menus and feedback.
- **Dynamic Help Menu**: Interactive, paginated help menu with customizable banners.
- **Local JSON Database**: Low-latency data persistence using an optimized in-memory cache system.
- **Automated Tasks**: Integrated `APScheduler` for background tasks and maintenance.

## Requirements

- Python 3.9 or higher
- API_ID & API_HASH from [my.telegram.org](https://my.telegram.org)
- BOT_TOKEN from [@BotFather](https://t.me/BotFather) (for Assistant features)

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/itswill00/Nebula_userbot.git
cd Nebula_userbot
```

### 2. Configure Environment
Create a `.env` file in the root directory:
```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
LOG_CHANNEL=your_log_channel_id
```

### 3. Setup and Run
```bash
bash setup.sh
bash run.sh
```

## Usage

Once the bot is online, you can use the `.help` command to explore available modules.

- `.help`: Triggers the interactive help menu via the Assistant Bot.
- `.alive`: Checks the current status of the engine.

## Code Standards

Nebula Engine adheres to high engineering standards:
- **PEP 8 Compliance**: Code is linted and formatted for readability.
- **Type Safety**: Explicit handling of types to ensure runtime stability.
- **Zero Gimmick**: Focused on functional utility without unnecessary overhead.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
