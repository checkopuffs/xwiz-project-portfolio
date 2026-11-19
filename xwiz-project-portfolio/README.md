# XWiz | IT, Homelab & Maker Projects

**Real-world IT infrastructure, local AI, embedded electronics, and 3D-printed prototypes.**

I work in IT support and build hands-on systems outside of work to learn how software, networking, virtualization, and hardware fit together. This repository is a living portfolio of projects I've deployed, repaired, prototyped, or am actively developing.

> **Portfolio status:** Some projects are operational; others are prototypes. Each project page marks its actual status and open work. This is a personal lab, not a production deployment guide.

## Featured work

| Project | What it demonstrates | Status | Explore |
| --- | --- | --- | --- |
| **XWiz AI + Telegram monitoring** | Python, SQLite, Telegram API, local LLMs, threaded workers, TCP health checks, reminders | **Running in my lab** (sample code included) | [Project + source](projects/xwiz-ai/README.md) |
| **Fedora + Proxmox homelab** | Docker, Linux, self-hosting, virtualization, service monitoring, troubleshooting | **In use** | [Infrastructure walkthrough](projects/homelab/README.md) |
| **Portable radar-inspired sensor** | ESP32-S3, HLK-LD2450 radar, UART, TFT UI, portable electronics | **Working prototype** | [Build story](projects/radar-sensor/README.md) |
| **Buddy Mini pixel pet** | ESP32-C3 concepts, ST7789 display, interaction design, Arduino, UI prototypes | **Prototype / hardware verification pending** | [Firmware + simulator](projects/buddy-mini/README.md) |
| **Cyberpunk speaker enclosure** | OpenSCAD, parametric CAD, mechanical fit, component reuse | **Unverified CAD prototype** | [OpenSCAD source](projects/cyberpunk-speaker/README.md) |

## Additional projects

- [Desktop robotic arm — V1 lessons and V2 goals](projects/robot-arm/README.md): ESP32/PCA9685, servo control, print-tolerance learning.
- [Batocera on a Dell laptop](projects/batocera/README.md): repurposed laptop, emulation troubleshooting and PS2 BIOS setup.

## Skills & technology

**Infrastructure:** Linux (Fedora, Ubuntu, Debian), Docker/Compose, Proxmox VE, basic network services, monitoring, backup planning.

**Programming & automation:** Python, Bash, SQLite, Arduino/C++, local LLM tooling (Ollama, Open WebUI), Telegram API, HTML/CSS/JavaScript prototypes.

**Hardware & fabrication:** ESP32-S3/C3, UART/SPI, radar and display modules, servo drivers, 3D printing, OpenSCAD, Bambu Lab P1S.

## Lab architecture (high level)

```text
                           Home LAN
                              |
                  +-----------+-----------+
                  |                       |
            Fedora + Docker         Proxmox nodes
            photos/media/DNS        VM / lab workloads
                  |                       |
                  +-----------+-----------+
                              |
                      Ubuntu AI host
                    Ollama + Open WebUI
                     Python Telegram bot
                              |
                      Read-only TCP checks

          Separate Debian NUC: Uptime Kuma availability dashboard
```

*This diagram is intentionally simplified and does not publish my real hostnames, addresses, credentials, or network topology.*

## How this repository is organized

```text
projects/
  xwiz-ai/             Python bot, configuration example, tests
  homelab/             Architecture, troubleshooting notes, audit script
  radar-sensor/        Hardware and status documentation
  buddy-mini/          Arduino firmware starter + browser UI prototype
  cyberpunk-speaker/   Parametric OpenSCAD design
  robot-arm/           Prototype lessons and next-version goals
  batocera/            Repurposed laptop and troubleshooting notes
.github/workflows/      Lightweight Python checks
PROFILE_README.md       Optional GitHub profile introduction
```

## Security & reuse

This public sample deliberately excludes tokens, keys, actual LAN IP addresses, private configurations, family details, and backup data. Copy the [example configuration](projects/xwiz-ai/.env.example) locally; **never commit a real `.env` file**. Some CAD/electrical designs have not been dimensionally or safety verified. Review and measure before using.

**Documentation is evolving.** Screenshots of finished builds and more source code can be added as projects are independently reviewed. Code and design rights are reserved unless a license is added later.
