# Portable radar-inspired sensor display

**Status:** **Working hardware prototype**, powered successfully from a USB power bank. Firmware is not included here yet because the exact final source file was not present in my saved project package.

## Build

- **Microcontroller:** ESP32-S3
- **Sensor:** HLK-LD2450 24 GHz radar module (target reports over UART)
- **Display:** 2.4-inch TFT
- **Power:** Portable USB power bank
- **Enclosure:** 3D-printed handheld housing; fit improvements are still needed

## Behavior demonstrated

- Black/green radar-inspired UI.
- Sweep animation, detected target markers, contact counts and distance labels.
- Changes to radar module orientation improved motion detection in real-world tests.
- A functioning portable assembled unit; a later unit was sold.

## Important limitations

This is a **radar-inspired visualization of the sensor's tracking data**, not a medical heartbeat monitor. The LD2450 is a presence/movement tracking radar; this prototype does not measure pulse or vital signs. Results depend on sensor placement and firmware filtering. Hardware photos, final wiring table and a cleaned version of the firmware are planned for a later revision.

## Next steps

- Publish a verified diagram for the exact TFT model and wiring used.
- Improve the enclosure fit and mounting angle.
- Add test footage and measured responsiveness before describing accuracy.
