# XWiz AI — Local assistant + Telegram monitoring

**Status:** Core Telegram bot, reminder commands, local LLM chat, and periodic TCP checks are in use in my homelab. Source here is a **sanitized, configurable sample** derived from the lab version, not a turnkey production service.

## Why I built it

I wanted a private AI helper for my home infrastructure with quick mobile access. I combined **Ollama + Open WebUI** with a Python Telegram bridge, using **SQLite** for persistent notes, reminders, and outage state.

## Implemented features

- Telegram private-chat restriction to a single configured user ID.
- Ollama-backed responses with limited recent chat context and notes.
- `/remember`, `/memories`, `/forget`, `/reset` for notes and message history.
- `/remind`, `/reminders`, `/cancel` for local-time reminders.
- `/status` for on-demand **TCP port checks**.
- `/monitor on|off` for periodic checks and outage/recovery notifications.
- State transition thresholds: **3 failures** to report down, **2 successes** to report recovery; retry of undelivered alerts.

> TCP reachability does not prove that a website, service or VM is fully healthy. It is not remote-control functionality.

## Source & safety

- [`xwiz_bot.py`](xwiz_bot.py) — original Python bot structure with private network details removed and targets moved to environment config.
- [`.env.example`](.env.example) — a **fake example** of the configuration format. Do not upload a real token or real `.env`.
- [`tests/`](tests/) — deterministic checks for reminder parsing and monitor transitions.

## Run a development instance

Python 3.10+ with IANA timezone data recommended (3.12 preferred). Python standard library only for this script.

```bash
cd projects/xwiz-ai
cp .env.example .env
# Fill in your own token and numeric user ID in .env, on your own machine.
# Export the variables through your shell / env loader before running:
set -a; source .env; set +a  # Bash/Zsh, trusted .env only
python xwiz_bot.py
```

The bot uses `OLLAMA_API_URL` (default `http://ollama:11434/api/chat`), so **that host must resolve and be reachable from the Python process**. On a stand-alone computer point it to your LAN-accessible, protected Ollama endpoint. The SQLite DB location is controlled with `XWIZ_DB_FILE`.

Do not open Ollama or Telegram credentials directly to the internet. Do not point monitors at systems you don't own or administer.

## Design notes

The reminder and monitor worker threads use their own SQLite connections. Alert delivery is retried, but this sample does **not** implement transactional outbox locking, deployment orchestration, structured logs, metrics, or comprehensive production security. Further work: tests for worker restart and queue recovery, config validation, dashboard integration, and hardware demos.
