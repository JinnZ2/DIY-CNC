# CNC-to-Metamaterial Modular Upgrade System

Transform a standard CNC into a bio-design and metamaterial manufacturing platform.

## System Overview

This project converts a precision desktop CNC into a modular metamaterial fabrication
platform — traditional machining and multi-material printing on one frame, aimed at
acoustic and structural work.

Built and documented here so anyone can copy it. Take what's useful, ignore the rest.
[Related Work](#related-work) lists other systems that solve similar problems, in case one
of them fits your situation better than this does.

## Core Architecture

### Existing CNC Platform

- 60” working area
- 8080 aluminum extrusion frame
- HGR20 linear guides, ball screws
- NEMA 23 stepper motors
- LinuxCNC control system

### Modular Metamaterial Upgrade

- Automated 30-taper tool changer (BT30 default — see [CNCToolchanger.md](./CNCToolchanger.md))
- Swappable print heads: metal, flexible, cavity, membrane
- Material handling: powder, filament, liquids, sheets
- Real-time quality control: acoustic + vision
- Custom fixtures for complex geometry and assembly

---

## Modules

### Print Head + Tool Changer System

- 8-position pneumatic tool changer
- 30-taper spindle adapter (must match the chosen taper standard)
- Metamaterial print heads (heated, precision)
- Fully integrated with LinuxCNC

### Materials Handling System

- Heated powder hoppers
- Filament spools and guides
- Syringe/liquid delivery systems
- Automated purge and feed routing

### Quality Control Integration

- Ultrasonic acoustic test module
- Structured light + camera vision system
- Automated pass/fail inspection
- Machine-integrated test cycles

### Specialized Workholding Fixtures

- Vacuum beds for soft materials
- Rotary vises for sculptural work
- Climate-controlled zones
- Assembly jigs for multi-part metamaterials

---

## Capabilities

### Traditional CNC Mode

- Wood, foam, aluminum, and plastic shaping
- Bio-inspired forms and 3D surfacing
- Rapid prototyping and fixture creation

### Metamaterial Mode

Ordered by how well the literature supports doing this on hobby-grade hardware:

- **Well demonstrated** — phononic crystals and gradient-index (GRIN) acoustic structures.
  Proof-of-concept GRIN lenses have been printed on desktop FDM machines; Luneburg lenses
  have been demonstrated for airborne sound (~8 kHz) and ultrasound (~40 kHz)
- **Well demonstrated** — embedded Helmholtz resonators, cavity arrays, and broadband
  sound absorbers
- **Research-grade** — acoustic cloaking. Real, but narrowband: experimental demonstrations
  sit around 3–8 kHz, and broadband 3D illusion cloaking is still an open problem. Treat as
  an experiment, not a capability the machine ships with

### Hybrid Mode

- Mixed materials and mixed physics
- Tool changes mid-process
- Fully integrated workflow for novel research

---

## Control Integration

- Custom G-codes for metamaterial commands
- Print head selection, temperature, flow control
- Automated part testing and verification
- Modular job loading and smart part sorting

---

## Related Work

Other people solving similar problems. If one of these fits your situation better, use it
instead — that's a better outcome than following this build out of loyalty.

**Machines**

- [Diabase H-Series](https://www.additivemanufacturing.media/articles/diabase-brings-a-machine-tool-perspective-to-fdm) — 10-position tool changer, up to 5 extruders, mills and prints. Closest commercial equivalent if you'd rather buy than build.
- [E3D ToolChanger](https://www.3dprintingindustry.com/news/review-e3d-motion-system-and-toolchanger-multitool-and-multi-material-3d-printer-186182/) — 4-position changer mixing extruders, lasers, and CNC tools. Discontinued, but the kinematic coupling design is worth studying.
- [smevirtual/hybrid-am](https://github.com/smevirtual/hybrid-am) — open-source hybrid FDM/CNC/laser on a Marlin-class controller.

**Control**

- [EMCRepRap](https://reprap.org/wiki/EMCRepRap) — the older approach to bolting an extruder onto LinuxCNC with custom M-codes and HAL. Single extruder, but the glue pattern still holds.
- [LinuxCNC additive forum](https://forum.linuxcnc.org/additive-manufacturing) — where the multi-extruder questions get worked out. Useful if you hit the same walls.
- [Hybrid FFF/CNC (2024)](https://www.sciencedirect.com/science/article/pii/S2468067224000300) — peer-reviewed open-source hybrid milling/printing toolchain.

**Background**

- [Fabricating 3D metamaterials with AM](https://www.mdpi.com/2504-4494/9/10/343) and [acoustic metamaterials review](https://www.sciencedirect.com/science/article/pii/S2590123026012740) — where the hard parts are, before you machine anything.

---

## Practical Limits

Things worth knowing before you cut material:

- **Frequency band.** Feature size is bounded by nozzle and end mill diameter, so this
  platform targets audible through low-ultrasonic structures (roughly 100 Hz – 40 kHz),
  which is where the printed-metamaterial literature lives. Optical, THz, and RF
  metamaterials need lithography and are out of reach here.
- **Surface finish matters.** FDM surface roughness and dimensional deviation measurably
  degrade acoustic performance. Plan to characterize parts rather than trust them.
- **Analogue gravity is analogue.** Phonons in hyperbolic metamaterials and Bose-Einstein
  condensates can model gravitational-wave and black-hole physics, and it's real research.
  But it simulates the mathematics — it doesn't generate or manipulate gravity, and that
  work needs ultracold atoms or EM metamaterials, not machinable acoustic structures. Don't
  expect to get there from here.

---

## Cost Summary

| Item                | Cost     | Source                                        |
|---------------------|----------|-----------------------------------------------|
| CNC Build Base      | ~$2,500  | Top of the $1,800–2,500 range in [CNC-build.md](./CNC-build.md) |
| Modular Upgrades    | ~$9,300  | Breakdown below                               |
| Total System Value  | ~$11,800 | Sum of the two                                |

### Upgrade Breakdown (~$9,300)

| Module                       | Cost    | Status                                     |
|------------------------------|---------|--------------------------------------------|
| Print Head + Tool Changer    | ~$4,400 | Itemized in [CNCToolchanger.md](./CNCToolchanger.md) |
| Materials Handling System    | —       | Not yet itemized                           |
| Quality Control Integration  | —       | Not yet itemized                           |
| Specialized Workholding      | —       | Not yet itemized                           |
| Remaining three modules      | ~$4,900 | Balance of the ~$9,300                     |

The ~$4,400 tool changer figure is included in the ~$9,300, not additional to it.

---

## Strategic Value

- **DIY Metamaterials:** Structures at home that otherwise need lab or vendor access
- **Research-Ready:** Bridge to acoustic and structural experimentation
- **Modular:** Upgrade and expand over time
- **Open Source:** Blueprint available for all, no vendor lock-in and no EOL date
