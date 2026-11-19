# Cyberpunk 3D-printed speaker enclosure

**Status:** Parametric CAD / fit-testing prototype; **not independently verified as a final print**.

A design experiment to reuse the **low-voltage speakers/drivers** from a Logitech S120 pair in a more distinctive 3D-printed housing.

- **Source:** [`xwiz_s120_cyberpunk_v1.scad`](xwiz_s120_cyberpunk_v1.scad)
- **Tooling:** OpenSCAD and a Bambu Lab P1S for eventual prints.
- **Design:** Modular shell, driver plate, rear panel, decorative rails and replaceable fit interfaces.

Preview in OpenSCAD with `part = "assembly"`; export individual parts by changing `part` and pressing **F6** for full render. Real driver and screw dimensions vary — measure your own parts before printing. The source was developed iteratively and may need mechanical corrections.

**Electrical safety:** These files are for low-voltage speaker driver enclosures only. Do **not** place exposed 120V AC mains wiring, transformers or PSU components inside a PLA/printed shell. If the existing powered speaker electronics require mains access or expose unsafe circuits, retain their intact approved enclosure or use an appropriately rated isolated low-voltage amplifier system.
