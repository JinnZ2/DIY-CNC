# CNC-to-Metamaterial Modular Upgrade System

Transform a standard CNC into a bio-design and metamaterial manufacturing platform.

## System Overview

This project converts a precision desktop CNC into a modular metamaterial fabrication
platform — traditional machining and multi-material printing on one frame, aimed at
acoustic and structural work.

This design was arrived at independently. Commercial multi-tool changers and hybrid
additive/subtractive platforms already existed (see [Prior Art](#prior-art)) — they just
weren't visible from here. Read that convergence as validation rather than as a correction:
people working separately, with different constraints, landed on the same architecture.
That is usually a sign the architecture is right.

What this build adds is the version you can source, assemble, and repair yourself — no
vendor in the loop, and no EOL date.

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

## Prior Art

**Scope: this section covers the mechanical architecture only.** The control layer is a
separate question and is treated below.

The mechanical side — a motion platform with a tool changer swapping between print heads and
cutting tools — has shipped commercially before. Listed here for orientation, not as a
retraction: the useful part is what can be borrowed from designs that already worked, and
what their fates suggest about owning your own.

| System | Relevance |
|--------|-----------|
| [E3D ToolChanger](https://www.3dprintingindustry.com/news/review-e3d-motion-system-and-toolchanger-multitool-and-multi-material-3d-printer-186182/) (2018–19) | 4-position changer explicitly mixing extrusion heads, laser engravers, CNC tools, and pick-and-place. Since discontinued — a good argument for owning the design rather than buying it |
| [Diabase H-Series](https://www.additivemanufacturing.media/articles/diabase-brings-a-machine-tool-perspective-to-fdm) (2019) | 10-position tool changer, up to 5 extruders, Hybrid model mills *and* prints. Closest commercial analogue to this build |
| [Hybrid additive/subtractive manufacturing](https://www.mdpi.com/2504-4494/9/10/343) | Mature industrial field — DED or LPBF paired with CNC finishing |
| [Multi-material AM for metamaterials](https://www.sciencedirect.com/science/article/pii/S2590123026012740) | Established review literature; precise material placement and interface control are the known hard parts |

On the mechanical side the differentiator is not novelty. It is sovereignty: sourceable
parts, a repairable frame, no vendor, and no EOL date.

### The Control Layer Is a Different Question

A search of the LinuxCNC ecosystem turns up much less:

| Prior work | What it covers |
|------------|----------------|
| [EMCRepRap](https://reprap.org/wiki/EMCRepRap) | Glue scripts bolting a *single* extruder to a CNC via custom M-codes and HAL. Closest match; long stale |
| [LinuxCNC forum, multiple extruders](https://forum.linuxcnc.org/38-general-linuxcnc-questions/34023-3d-printer-with-multiple-extruders) | Discussion of running extruders as A/B/C axes and rerouting stepper IO on `M6` — open questions, not a released system |
| [Hybrid FFF/CNC (2024)](https://www.sciencedirect.com/science/article/pii/S2468067224000300) | Peer-reviewed open-source hybrid milling/printing — but built on the E3D ToolChanger's own firmware, not LinuxCNC |
| [smevirtual/hybrid-am](https://github.com/smevirtual/hybrid-am) | Hobbyist hybrid FDM/CNC/laser on a Marlin-class controller, not LinuxCNC |

No released example was found of LinuxCNC driving automatically tool-changed, multi-head
print heads through a purpose-built M-code vocabulary. That is an absence of evidence, not
proof of primacy — but it is where the interesting work in this project sits, and it is the
part these docs currently describe in the least detail.

---

## Scope of Claims

- **Frequency band.** Feature size is bounded by nozzle and end mill diameter, so this
  platform targets audible through low-ultrasonic structures (roughly 100 Hz – 40 kHz),
  which is where the printed-metamaterial literature lives. Optical, THz, and RF
  metamaterials need lithography and are out of reach here.
- **Surface finish matters.** FDM surface roughness and dimensional deviation measurably
  degrade acoustic performance. Expect to characterize parts, not trust them.
- **On "acoustic gravity."** Analogue gravity is a legitimate research field — phonons in
  hyperbolic metamaterials and Bose-Einstein condensates can model gravitational-wave and
  black-hole physics. But it is *analogue*: it simulates the mathematics, it does not
  generate or manipulate gravity. That work also lives in hyperbolic EM metamaterials and
  ultracold atoms, not in machinable acoustic structures. Nothing on this machine reaches
  it, and earlier wording in these docs implied otherwise.

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
