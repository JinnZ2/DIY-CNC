# Legacy — Superseded Claims and Why They Changed

Nothing in this folder is current. It's kept because the *process* of being wrong and
correcting it is worth more to a future builder than the corrected answer alone.

If you're building from these docs, read the current files. If you're wondering how much to
trust them, read this.

---

## The Method

This is just the scientific method applied to a build log:

1. **Claim** something, based on what you know at the time
2. **Test** it against the literature and against what's already shipping
3. **Falsify** what doesn't hold
4. **Revise** the claim to match the evidence
5. **Record what's still unknown** — the open questions are the useful part
6. **Rerun** when new information arrives

The failure mode isn't being wrong. It's being wrong and never checking, or checking and
quietly editing so nobody can see the correction happened. Hence this folder.

A claim made honestly from limited information isn't a lie — it's a hypothesis. It just has
to stay open to testing.

---

## Claims Ledger

### 1. "The world's first modular metamaterial fabrication system"

- **Claimed:** July 2025
- **Tested:** August 2026, against commercial products and AM literature
- **Result: FALSIFIED**

Prior art existed on every axis. [E3D ToolChanger](https://www.3dprintingindustry.com/news/review-e3d-motion-system-and-toolchanger-multitool-and-multi-material-3d-printer-186182/)
(2018–19) shipped a 4-position changer explicitly mixing extrusion heads, laser engravers,
and CNC tools. [Diabase H-Series](https://www.additivemanufacturing.media/articles/diabase-brings-a-machine-tool-perspective-to-fdm)
(2019) shipped a 10-position changer that both mills and prints. Hybrid additive/subtractive
manufacturing is a mature industrial field.

**Revised to:** no primacy claim at all, plus a Related Work section pointing builders at
the alternatives.

**Worth noting:** the claim was honest when written. Those systems weren't visible from
here — no reliable internet, building alone. Arriving independently at an architecture
several other people also arrived at is evidence the architecture is sound. It just isn't
a first.

### 2. "Cloaking, energy capture, acoustic gravity tools"

- **Result: PARTIALLY FALSIFIED**

| Sub-claim | Outcome |
|-----------|---------|
| Cloaking | Real but narrowband — demonstrations sit around 3–8 kHz, broadband 3D illusion cloaking is still open. Downgraded from capability to experiment |
| Energy capture | No supporting evidence found. Removed |
| Acoustic gravity | Analogue gravity is legitimate physics, but it *models* gravitational behavior rather than manipulating gravity, and the work lives in ultracold atoms and hyperbolic EM metamaterials — not machinable acoustic parts. Removed as a capability, kept as a caution |

### 3. Phononic and gradient-index fabrication

- **Result: CONFIRMED**

GRIN acoustic lenses have been printed on desktop FDM hardware; Luneburg lenses are
demonstrated for airborne sound (~8 kHz) and ultrasound (~40 kHz). This one held up, and
the current doc now grades capabilities by how well the literature supports them.

### 4. ISO30 vs BT30 spindle taper

- **Result: RECONCILED** (internal inconsistency, not a literature question)

Three docs specified different tapers. `CNCToolchanger.md` is now the authority — BT30
default, ISO30 budget alternative — and carries a warning that the two are not
interchangeable, since every custom print head adapter gets machined to whichever you pick.

### 5. Cost figures: ~$4,400 vs ~$9,300

- **Result: NOT ACTUALLY IN CONFLICT**

The $4,400 tool changer figure is module one of the $9,300 upgrade, not a competing total.
No numbers changed — only the relationship between them was made explicit. Worth logging
because "these two numbers disagree" turned out to be a documentation gap, not an error.

---

## Still Open

The honest unknowns, recorded so they can be tested later:

- **The control layer.** A search of the LinuxCNC ecosystem turned up only a stale
  single-extruder glue project ([EMCRepRap](https://reprap.org/wiki/EMCRepRap)), unresolved
  forum discussion, and hybrid work built on other firmware stacks. No released example of
  LinuxCNC driving automatically tool-changed multi-head print heads through a purpose-built
  M-code vocabulary. That is **absence of evidence, not proof of primacy** — and the code
  isn't in this repo, so it can't be verified from here either way.
- **The remaining ~$4,900** across materials handling, quality control, and workholding has
  never been itemized.
- **Component pricing** throughout dates from mid-2025 and hasn't been re-sourced.

---

## Files Here

| File | What it is |
|------|------------|
| `2025-07-CNC-metamaterial-build.md` | The original document as committed, verbatim. Contains the falsified claims above |
