# Buddy Mini — interactive pixel pet

**Status:** **Software / firmware starter prototype**. Parts have been ordered; end-to-end hardware verification has not yet been completed.

An interactive cat/pet concept built around a **1.54-inch 240×240 ST7789 SPI color TFT**. The planned device adds simple games, encouraging quotes, button interactions and custom graphics.

## What is included

- [`firmware/Buddy_Mini_Starter/Buddy_Mini_Starter.ino`](firmware/Buddy_Mini_Starter/Buddy_Mini_Starter.ino) — Arduino firmware **starter originally targeted to the Seeed XIAO ESP32-C3 board**. Not tested on a connected device.
- [`simulator/buddy-mini-v02.html`](simulator/buddy-mini-v02.html) — browser-based concept preview, separate from microcontroller code.

## Hardware caution and compatibility

The final ordered board is an **ESP32-C3 Super Mini**, which is **not pin-compatible** with the XIAO ESP32-C3. The included firmware uses XIAO `D1`, `D2`, etc. labels and **must be remapped and tested** for the actual board. Do not copy the wiring as-is to an ESP32-C3 Super Mini. LCD supply and backlight requirements must also be verified from the exact seller's datasheet.

Start with safe USB power and a breadboard. Do not connect LiPo cells directly to ESP32 or TFT 3V3 without the correct charger/protection/regulated power path. Do not use uncertified or unverified battery wiring.

## Planned additions

Petting/touch sensor, haptics or audio feedback, a safe rechargeable battery design, persistent pet statistics, final printed keychain shell and hardware validation.

**Privacy:** The public sample uses a generic pet name rather than a child's name or personal family messages. The artwork is an original cat motif, not licensed character assets.
