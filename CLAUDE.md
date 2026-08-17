# CLAUDE.md — AI Assistant Guide for DIY-CNC

## Project Overview

This repository contains build specifications, design philosophy, and **helper scripts** for a DIY CNC machine and modular metamaterial fabrication system. No build system or CI/CD pipeline — the project is documentation plus standalone Python utilities.

**Owner:** JinnZ2
**License:** MIT (2025)

## Repository Structure

```
DIY-CNC/
├── CLAUDE.md                    # This file — AI assistant guide
├── README.md                    # Project overview and scope statement
├── SCOPE.md                     # Scaling philosophy ("lichen model")
├── CNC-build.md                 # CNC machine build guide (two options)
├── CNC-metamaterial-build.md    # Modular metamaterial upgrade system
├── CNCToolchanger.md            # Tool changer & print head integration
├── LICENSE                      # MIT License
└── scripts/                     # Python helper utilities (stdlib only)
    ├── hardware_sourcer.py      # Find parts locally, track suppliers & salvage subs
    ├── measurement_helper.py    # Precision measuring with imprecise tools
    ├── bom_calculator.py        # Bill of materials tracker with budget impact
    ├── cut_optimizer.py         # Cut list optimizer to minimize extrusion waste
    └── linuxcnc_config.py       # LinuxCNC INI/HAL config file generator
```

## Document Descriptions

| File | Purpose |
|------|---------|
| `README.md` | Brief scope statement and link to philosophy |
| `SCOPE.md` | "Lichen model" scaling philosophy — autonomy, sufficiency, offline-first |
| `CNC-build.md` | Two build paths: Option A (~$300-600 GRBL prototype) and Option B (~$1,800-2,500 LinuxCNC precision build). Includes frame dimensions, motion system specs, electronics stack, and assembly strategy |
| `CNC-metamaterial-build.md` | Modular upgrade converting CNC into metamaterial fabrication platform. Covers print heads, materials handling, quality control, and workholding (~$9,300 upgrade, ~$11,800 total) |
| `CNCToolchanger.md` | BT30 automatic tool changer specs, print head mounting interface, LinuxCNC M-code integration, cable routing, and assembly timeline |

## Key Technical Specs (Quick Reference)

- **Frame:** 8080/8040 aluminum extrusion, 60" working width
- **Motion:** HGR20 linear guides, 1605/1204 ball screws
- **Motors:** NEMA 23 (3Nm) with DM542 drivers
- **Control:** LinuxCNC on dedicated PC (Mesa 7i76e board)
- **Spindle:** Palm router upgradeable to BT30/ISO30 ATC
- **Tool Changer:** 8-position pneumatic carousel
- **Custom M-Codes:** M6 (tool change), M150 (print head select), M151 (extrusion temp), M153/M154 (prime/retract)

## Design Philosophy & Conventions

**Core principles to respect in all contributions:**

1. **Fit-for-purpose sufficiency** — no bloat, no over-engineering, no corporate scaling
2. **Offline-first** — everything must work without internet
3. **Autonomy and sovereignty** — users own their tools completely
4. **Minimal dependencies** — avoid unnecessary external requirements
5. **Modular and repairable** — designed for upgrade paths, not disposability
6. **Building over documenting** — documentation is pragmatic, not polished

## Writing Style & Formatting

- Markdown throughout; no HTML unless necessary
- Tables use pipe (`|`) format for component specs
- Bullet lists preferred for specifications and part lists
- Straightforward, practical tone — no marketing language or hype
- Emoji usage is acceptable in headers (existing docs use them sparingly)
- Documents reference future files that may not exist yet (e.g., `/docs/metamaterial_extension.md`)

## Helper Scripts (`scripts/`)

All scripts are **Python 3 stdlib only** — zero pip installs, fully offline. Each has both an interactive menu and CLI flags.

| Script | Purpose | Run |
|--------|---------|-----|
| `hardware_sourcer.py` | Local parts database with suppliers, salvage alternatives, and substitution options. Seeds from CNC-build.md specs. SQLite-backed. | `python scripts/hardware_sourcer.py` |
| `measurement_helper.py` | Squareness checks, leveling, repeated-measurement statistics, tool calibration, 3-4-5 method, unit conversion. No database. | `python scripts/measurement_helper.py` |
| `bom_calculator.py` | Full BOM for Options A, B, and Metamaterial. Track acquisitions, generate shopping lists, export CSV/JSON. SQLite-backed. | `python scripts/bom_calculator.py` |
| `cut_optimizer.py` | First-fit-decreasing bin packing for extrusion cuts. Compares stock lengths, accounts for saw kerf, visual cut diagrams. | `python scripts/cut_optimizer.py` |
| `linuxcnc_config.py` | Generates INI, HAL, tool table, and postgui files for Mesa 7i76e or parallel port setups based on your motor/screw/driver choices. | `python scripts/linuxcnc_config.py` |

**Generated files** (databases, exports, LinuxCNC output) are gitignored — they contain user-specific data.

## What AI Assistants Should Know

1. **No build/test/lint commands** — scripts run directly with `python3`, no setup required
2. **Stdlib only** — never add pip dependencies; sqlite3 is part of stdlib
3. **Do not add unnecessary tooling** (package.json, linters, CI) unless explicitly asked
4. **Respect the minimalist ethos** — don't suggest scaling, SaaS patterns, or enterprise tooling
5. **Keep specs accurate** — component specifications, dimensions, and costs are carefully chosen
6. **Preserve the project's voice** — direct, practical, sovereignty-focused
7. **Tables may render imperfectly** — some docs have formatting notes about mobile editing; don't "fix" intentional formatting guidance
8. **The project is a seed, not a startup** — treat it accordingly
9. **Script databases are user data** — never commit `.db`, `.csv`, `.json` exports, or `linuxcnc_output/`
