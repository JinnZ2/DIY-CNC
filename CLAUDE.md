# CLAUDE.md — AI Assistant Guide for DIY-CNC

## Project Overview

This is a **documentation-only repository** containing build specifications and design philosophy for a DIY CNC machine and modular metamaterial fabrication system. There is no source code, build system, or CI/CD pipeline — the entire repository consists of markdown files.

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
├── legacy/                      # Superseded claims + why they changed
│   ├── README.md                # The method, claims ledger, open questions
│   └── 2025-07-CNC-metamaterial-build.md   # Original doc, verbatim
└── LICENSE                      # MIT License
```

No code, no config files, no `.gitignore`. One subdirectory (`legacy/`), which is an
archive — never edit its contents to match current specs. It is deliberately out of date.

## Document Descriptions

| File | Purpose |
|------|---------|
| `README.md` | Brief scope statement and link to philosophy |
| `SCOPE.md` | "Lichen model" scaling philosophy — autonomy, sufficiency, offline-first |
| `CNC-build.md` | Two build paths: Option A (~$300-600 GRBL prototype) and Option B (~$1,800-2,500 LinuxCNC precision build). Includes frame dimensions, motion system specs, electronics stack, and assembly strategy |
| `CNC-metamaterial-build.md` | Modular upgrade converting CNC into metamaterial fabrication platform. Covers print heads, materials handling, quality control, and workholding (~$9,300 upgrade, ~$11,800 total) |
| `CNCToolchanger.md` | BT30 automatic tool changer specs, print head mounting interface, LinuxCNC M-code integration, cable routing, and assembly timeline ($3,450–5,400, ~$4,400 midpoint — this is the first module of the ~$9,300 upgrade, not additional to it) |

| `legacy/README.md` | Claims that were tested and falsified, what replaced them, and the open questions. Kept so the revision process is visible, not just its output |

**Authority for conflicting specs:** `CNCToolchanger.md` is the source of truth for the
spindle taper standard (BT30 default, ISO30 budget alternative) and for tool changer costs.
The other docs say "30-taper" and link to it rather than restating a standard.

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

## What AI Assistants Should Know

1. **No build/test/lint commands exist** — this is pure documentation
2. **Do not add unnecessary tooling** (package.json, linters, CI) unless explicitly asked
3. **Respect the minimalist ethos** — don't suggest scaling, SaaS patterns, or enterprise tooling
4. **Keep specs accurate** — component specifications, dimensions, and costs are carefully chosen
5. **Preserve the project's voice** — direct, practical, sovereignty-focused
6. **Tables may render imperfectly** — some docs have formatting notes about mobile editing; don't "fix" intentional formatting guidance
7. **The project is a seed, not a startup** — treat it accordingly
