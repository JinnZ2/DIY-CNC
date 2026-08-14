# CNC-to-Metamaterial Modular Upgrade System

Transform a standard CNC into a bio-design and metamaterial manufacturing platform.

## System Overview

This project converts a precision desktop CNC into the world’s first modular metamaterial fabrication system. It supports both traditional machining and next-gen material printing for advanced acoustic, structural, and energy research.

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

- Fabrication of phononic/gradient-index materials
- Embedded resonators and bubble cavities
- Cloaking, energy capture, acoustic gravity tools

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

- **DIY Metamaterials:** Make advanced structures at home
- **Research-Ready:** Bridge to acoustic, gravity, or energy exploration
- **Modular:** Upgrade and expand over time
- **Open Source:** Blueprint available for all
