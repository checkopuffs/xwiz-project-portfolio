# Desktop robotic arm — V1 lessons / V2 design study

**Status:** V1 assembled and achieved motion, but mechanics and responsiveness fell short of the design goal. V2 is **planning**, not a completed build.

## Hardware explored

ESP32 controller, PCA9685 PWM servo board, multiple hobby servos (including MG996R/MG995/SG90/MG90S), external 5 V supply, and 3D printed brackets.

## Lessons learned

- Basic movement is not the same thing as a reliable manipulator.
- Printed bracket alignment and servo shaft/ear measurements must be validated against the exact actuator.
- Small-angle moves looked underwhelming and the first arm felt slow/wobbly.
- Mechanically unverified CAD should be labelled prototypes instead of production-ready printable parts.

## V2 goals (not achieved yet)

A sturdier printed arm with approximately four to six actuators, ~250–300 g phone payload target, more responsive motion, broad base rotation, and Wi-Fi + remote-control options. Actual torque, kinematics, gearboxes and power capacity require engineering checks before claims can be made.

See [`mechanical-notes.md`](mechanical-notes.md) for an early base design draft. The dimensions are *not* verified against every servo variant.
