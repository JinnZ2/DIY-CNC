
# CNC Tool Changer & Print Head Integration

## Overview

This guide provides detailed specifications and integration instructions for converting a desktop CNC into a multi-material manufacturing platform using a BT30 automatic tool changer and modular print head system. It supports metamaterial, prosthetic, and advanced composite production.

---

## Tool Changer System Options

### Option 1: BT30 Automatic Tool Changer (Recommended)

**Why BT30:** Perfect size for desktop CNC, strong enough for print heads, widely available

**Core Components:**

- **Spindle:** BT30 pneumatic spindle (3HP, 24,000 RPM)
- **Tool Changer:** Pneumatic umbrella-style ATC
- **Tool Holders:** BT30 toolholders with custom print head adapters
- **Tool Carousel:** 8-position fixed rack

### Option 2: ISO30 Manual+ System (Budget Alternative)

Manual swap toolchanger for reduced cost and simplified integration.

### Pick the Taper Standard First

BT30 and ISO30 are both 7:24 #30 tapers, but their retention knobs (pull studs) and
flange/drive geometry differ — holders are **not** interchangeable between them. Every
custom print head adapter is machined to whichever standard you pick, so decide before
cutting any adapters or ordering tool holders.

This repo treats **BT30 as the default** (Option 1). Where the other build docs say
"30-taper," this file is the authority on which standard is meant.

---

## Print Head Mounting Interface Design

### Universal Print Head Adapter

- **Shank:** BT30/ISO30, precision-ground
- **Interface Plate:** 50mm x 50mm bolt circle, 20mm center hole
- **Material:** Aluminum 6061-T6

### Print Head Types

1. **Metal Powder Extruder**
2. **Flexible Material Extruder (TPU, Silicone)**
3. **Cavity Generator (for bubble-in-sphere structures)**

---

## Mechanical Integration

### Z-Axis Modification

- **Spindle Mount Plate:** Aluminum 6061, 20mm thick
- **Load Capacity:** Compatible with HGR20 guides and 5kg dynamic load

### Tool Rack

- **Y-Axis Rail Mount or Fixed Side Mount**
- **8 Tool Positions**
- **Pneumatic Clearance: 200mm**

---

## Cable and Pneumatic Routing

- **Cable Chain:** 25mm x 38mm
- **Wiring:** 24V heater, 5V signals, RS485, stepper control
- **Pneumatics:** 4mm-6mm air and vacuum lines

---

## Control System Integration

### LinuxCNC Configuration

- **I/O:** Spindle orientation, solenoids, sensors
- **M-Codes:**
    - `M6 Txx` – Tool change
    - `M150` – Select print head
    - `M151` – Set extrusion temp
    - `M153/M154` – Prime/retract

### Print Head Controllers

- **Main:** LinuxCNC PC
- **Secondary:** Arduino Mega (RS485)
- **Drivers:** TMC2209
- **Sensors:** PT100 + Thermistor

---

## Assembly Instructions

### Weekend 1

- Modify Z-axis
- Install spindle and tool rack

### Weekend 2

- Assemble print head adapters
- Route cabling
- Configure control system

---

## Suppliers

- **Spindle/ATC:** CNC-TEKNIK, Automation Direct
- **Extruders:** Bondtech, E3D, Slice Engineering
- **Wiring & Components:** McMaster, Misumi, Adafruit

---

## Cost Summary

| Item               | Range         |
|--------------------|---------------|
| Tool Changer System| $1,750–2,750  |
| Print Head System  | $1,150–1,800  |
| Install Hardware   | $550–850      |
| **Total**          | **$3,450–5,400** (~$4,400 midpoint) |

This ~$4,400 is the *Print Head + Tool Changer* module only. It is the first of the four
modules in [CNC-metamaterial-build.md](./CNC-metamaterial-build.md), whose ~$9,300 upgrade
figure includes it — the two numbers are not alternatives to each other.

---

## Next Steps

1. Measure Z-axis compatibility
2. Choose toolchanger type
3. Order spindle/ATC
4. Build extruder head
5. Validate tool change sequences
6. Begin advanced material testing

---

*For advanced metamaterial print sequences, coupling simulation, and modular expansion logic, see `/docs/metamaterial_extension.md` (coming soon).*
