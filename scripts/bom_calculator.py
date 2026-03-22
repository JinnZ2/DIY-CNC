#!/usr/bin/env python3
"""
BOM Calculator — Bill of Materials tracker for DIY CNC builds.

Generates shopping lists from the build specs, tracks what you've
acquired vs. what's left, lets you swap parts and see budget impact.

Usage:
    python bom_calculator.py                   # Interactive mode
    python bom_calculator.py show              # Show full BOM
    python bom_calculator.py show --option a   # Show Option A BOM
    python bom_calculator.py show --option b   # Show Option B BOM
    python bom_calculator.py summary           # Budget summary
    python bom_calculator.py export            # Export to CSV
"""

import argparse
import csv
import json
import os
import sqlite3
import sys
from pathlib import Path

DB_NAME = "bom_tracker.db"


def get_db_path():
    return Path(__file__).parent / DB_NAME


def init_db(conn):
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bom_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            spec TEXT,
            qty INTEGER DEFAULT 1,
            unit_price_low REAL DEFAULT 0,
            unit_price_high REAL DEFAULT 0,
            build_option TEXT DEFAULT 'both',
            acquired INTEGER DEFAULT 0,
            acquired_price REAL,
            acquired_source TEXT,
            notes TEXT
        )
    """)

    c.execute("SELECT COUNT(*) FROM bom_items")
    if c.fetchone()[0] == 0:
        _seed_bom(c)

    conn.commit()


def _seed_bom(cursor):
    """Seed BOM from CNC-build.md and CNC-metamaterial-build.md specs."""
    items = [
        # Option A: Proof-of-Concept (~$300-600)
        ("Drawer Slides (linear rails)", "motion", "Pair", 3, 8, 15, "a", "Salvageable from furniture"),
        ("NEMA 17 Stepper Motor", "electronics", "Standard", 3, 10, 20, "a", "3D printer community"),
        ("Threaded Rod + Nuts", "motion", "M8 x 500mm", 3, 3, 8, "a", "DIY lead screws"),
        ("Arduino Uno", "electronics", "R3", 1, 10, 25, "a", None),
        ("GRBL Shield", "electronics", "CNC Shield V3", 1, 5, 15, "a", None),
        ("A4988 Stepper Driver", "electronics", "Module", 3, 2, 5, "a", None),
        ("Handheld Router", "spindle", "DeWalt or similar", 1, 60, 100, "a", None),
        ("8020 Aluminum Extrusion", "frame", "Misc lengths", 1, 50, 100, "a", "Lot/bundle price"),
        ("Plywood Base", "frame", "3/4\" sheet", 1, 20, 40, "a", None),
        ("Skateboard Bearings", "motion", "608ZZ", 12, 0.50, 2, "a", "Linear support"),
        ("Wiring & Connectors", "electronics", "Kit", 1, 15, 30, "a", None),
        ("Power Supply 12V", "electronics", "12V 5A", 1, 10, 20, "a", None),

        # Option B: Precision Build (~$1,800-2,500)
        ("8080 Extrusion 72\"", "frame", "8080 x 72\"", 2, 40, 80, "b", "X-axis base rails"),
        ("8080 Extrusion 52\"", "frame", "8080 x 52\"", 2, 30, 60, "b", "Y-axis cross rails"),
        ("8040 Extrusion 30\"", "frame", "8040 x 30\"", 4, 15, 35, "b", "Vertical posts"),
        ("8040 Extrusion 60\"", "frame", "8040 x 60\"", 4, 25, 50, "b", "Gantry + bracing"),
        ("8040 Extrusion 40\"", "frame", "8040 x 40\"", 2, 20, 40, "b", "Y-axis support"),
        ("Cast Brackets + Gussets", "frame", "Standard", 20, 2, 8, "b", None),
        ("T-Slot Hardware", "frame", "M8x20mm", 100, 0.15, 0.50, "b", "Nuts + bolts"),
        ("Ball Screw 1605 x 2000mm", "motion", "1605 x 2000mm", 1, 40, 120, "b", "X-axis"),
        ("Ball Screw 1605 x 1500mm", "motion", "1605 x 1500mm", 1, 35, 100, "b", "Y-axis"),
        ("Ball Screw 1204 x 500mm", "motion", "1204 x 500mm", 1, 20, 60, "b", "Z-axis"),
        ("HGR20 Linear Guide 2000mm", "motion", "HGR20 x 2000mm", 2, 30, 90, "b", "X-axis + blocks"),
        ("HGR20 Linear Guide 1500mm", "motion", "HGR20 x 1500mm", 2, 25, 75, "b", "Y-axis + blocks"),
        ("HGR15 Linear Guide 500mm", "motion", "HGR15 x 500mm", 2, 15, 45, "b", "Z-axis + blocks"),
        ("Pillow Blocks", "motion", "Standard", 6, 5, 20, "b", None),
        ("Flexible Couplings", "motion", "5-10mm", 3, 3, 12, "b", None),
        ("NEMA 23 Stepper Motor", "electronics", "3Nm", 3, 15, 40, "b", None),
        ("DM542 Stepper Driver", "electronics", "DM542", 3, 15, 35, "b", None),
        ("Mesa 7i76e", "electronics", "7i76e", 1, 200, 300, "b", "LinuxCNC controller"),
        ("48V Power Supply", "electronics", "48V 10A", 1, 25, 60, "b", None),
        ("Dedicated PC", "electronics", "LinuxCNC compatible", 1, 50, 200, "b", "Used/refurb OK"),
        ("Palm Router", "spindle", "DeWalt DWP611", 1, 80, 130, "b", "Upgradeable"),
        ("Router Clamp Mount", "spindle", "Adjustable", 1, 15, 40, "b", None),
        ("Cable Chain", "wiring", "25x38mm", 3, 10, 30, "b", "Meters"),
        ("Wiring Kit", "wiring", "24V/5V/signal", 1, 30, 60, "b", None),

        # Metamaterial Upgrade Module
        ("BT30 Pneumatic Spindle", "toolchanger", "3HP 24000RPM", 1, 400, 800, "meta", None),
        ("Pneumatic ATC Unit", "toolchanger", "Umbrella-style", 1, 300, 600, "meta", "8-position"),
        ("BT30 Tool Holders", "toolchanger", "BT30", 8, 15, 40, "meta", None),
        ("Print Head Adapter Plates", "toolchanger", "Al 6061-T6", 4, 20, 50, "meta", "Custom machined"),
        ("Metal Powder Extruder", "printhead", "Custom", 1, 150, 300, "meta", None),
        ("Flexible Material Extruder", "printhead", "TPU/Silicone", 1, 100, 200, "meta", None),
        ("Cavity Generator Head", "printhead", "Custom", 1, 100, 250, "meta", None),
        ("Heated Powder Hopper", "materials", "Custom", 1, 80, 150, "meta", None),
        ("Syringe Delivery System", "materials", "Precision", 1, 50, 100, "meta", None),
        ("Ultrasonic Test Module", "qc", "Acoustic", 1, 200, 400, "meta", None),
        ("Camera Vision System", "qc", "Structured light", 1, 100, 300, "meta", None),
        ("Vacuum Bed", "fixtures", "For soft materials", 1, 80, 200, "meta", None),
        ("Spindle Mount Plate", "toolchanger", "Al 6061 20mm", 1, 30, 80, "meta", "Z-axis mod"),
        ("Pneumatic Supply", "toolchanger", "Compressor + lines", 1, 100, 250, "meta", None),
    ]

    for item in items:
        cursor.execute(
            "INSERT INTO bom_items (name, category, spec, qty, unit_price_low, unit_price_high, "
            "build_option, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", item
        )


# --- Display ---

def show_bom(conn, option=None, show_acquired=None):
    """Display the BOM, optionally filtered."""
    c = conn.cursor()

    where = []
    params = []
    if option:
        if option == "a":
            where.append("build_option IN ('a', 'both')")
        elif option == "b":
            where.append("build_option IN ('b', 'both')")
        elif option == "meta":
            where.append("build_option = 'meta'")
        elif option == "full":
            where.append("build_option IN ('b', 'both', 'meta')")
    if show_acquired is not None:
        where.append("acquired = ?")
        params.append(1 if show_acquired else 0)

    query = "SELECT * FROM bom_items"
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY category, name"

    c.execute(query, params)
    items = c.fetchall()
    cols = [d[0] for d in c.description]

    if not items:
        print("\n  No items found.")
        return

    current_cat = None
    total_low = 0
    total_high = 0
    total_acquired = 0

    option_labels = {"a": "Option A", "b": "Option B", "both": "Both", "meta": "Metamaterial", "full": "Full System"}
    label = option_labels.get(option, "All Options")
    print(f"\n  BOM — {label}")
    print(f"  {'=' * 70}")

    for row in items:
        item = dict(zip(cols, row))
        cat = item["category"]

        if cat != current_cat:
            current_cat = cat
            print(f"\n  [{cat.upper()}]")

        qty = item["qty"]
        plow = item["unit_price_low"] * qty
        phigh = item["unit_price_high"] * qty
        total_low += plow
        total_high += phigh

        status = ""
        if item["acquired"]:
            status = " [ACQUIRED"
            if item["acquired_price"]:
                status += f" ${item['acquired_price']:.2f}"
                total_acquired += item["acquired_price"]
            if item["acquired_source"]:
                status += f" from {item['acquired_source']}"
            status += "]"

        notes = f"  ({item['notes']})" if item["notes"] else ""
        print(f"    {item['name']:<35s} x{qty:<3d} ${plow:>7.0f}-${phigh:<7.0f}{status}{notes}")

    print(f"\n  {'─' * 70}")
    print(f"  Estimated Total:  ${total_low:,.0f} — ${total_high:,.0f}")
    if total_acquired > 0:
        print(f"  Already Spent:    ${total_acquired:,.2f}")
        remaining_low = max(0, total_low - total_acquired)
        remaining_high = max(0, total_high - total_acquired)
        print(f"  Remaining:        ${remaining_low:,.0f} — ${remaining_high:,.0f}")


def budget_summary(conn):
    """Show budget breakdown by build option and category."""
    c = conn.cursor()

    for option, label in [("a", "Option A (Prototype)"), ("b", "Option B (Precision)"),
                          ("meta", "Metamaterial Upgrade")]:
        if option == "a":
            c.execute("SELECT category, SUM(qty * unit_price_low), SUM(qty * unit_price_high) "
                      "FROM bom_items WHERE build_option IN ('a', 'both') GROUP BY category")
        elif option == "b":
            c.execute("SELECT category, SUM(qty * unit_price_low), SUM(qty * unit_price_high) "
                      "FROM bom_items WHERE build_option IN ('b', 'both') GROUP BY category")
        else:
            c.execute("SELECT category, SUM(qty * unit_price_low), SUM(qty * unit_price_high) "
                      "FROM bom_items WHERE build_option = 'meta' GROUP BY category")

        rows = c.fetchall()
        if not rows:
            continue

        total_low = sum(r[1] for r in rows)
        total_high = sum(r[2] for r in rows)

        print(f"\n  {label}")
        print(f"  {'─' * 45}")
        for cat, low, high in rows:
            print(f"    {cat:<20s} ${low:>7,.0f} — ${high:>,.0f}")
        print(f"    {'TOTAL':<20s} ${total_low:>7,.0f} — ${total_high:>,.0f}")

    # Full system
    c.execute("SELECT SUM(qty * unit_price_low), SUM(qty * unit_price_high) "
              "FROM bom_items WHERE build_option IN ('b', 'both', 'meta')")
    row = c.fetchone()
    if row and row[0]:
        print(f"\n  Full System (Option B + Metamaterial)")
        print(f"  {'─' * 45}")
        print(f"    {'TOTAL':<20s} ${row[0]:>7,.0f} — ${row[1]:>,.0f}")


# --- Modify ---

def mark_acquired_interactive(conn):
    """Mark an item as acquired."""
    c = conn.cursor()
    print("\n  --- Mark Item as Acquired ---\n")
    q = input("  Search for item: ").strip()
    if not q:
        return

    c.execute("SELECT id, name, spec, qty, acquired FROM bom_items WHERE name LIKE ? OR spec LIKE ?",
              (f"%{q}%", f"%{q}%"))
    items = c.fetchall()
    if not items:
        print(f"  No items matching '{q}'")
        return

    for pid, name, spec, qty, acq in items:
        status = " [ACQUIRED]" if acq else ""
        print(f"    [{pid}] {name} ({spec}) x{qty}{status}")

    try:
        pid = int(input("\n  Item ID: ").strip())
        price = input("  Price paid ($, blank to skip): ").strip()
        price = float(price) if price else None
        source = input("  Source (where you got it): ").strip() or None
    except (ValueError, EOFError):
        print("  Cancelled.")
        return

    c.execute("UPDATE bom_items SET acquired = 1, acquired_price = ?, acquired_source = ? WHERE id = ?",
              (price, source, pid))
    conn.commit()
    print("  Marked as acquired.")


def add_item_interactive(conn):
    """Add a custom item to the BOM."""
    print("\n  --- Add BOM Item ---\n")
    name = input("  Item name: ").strip()
    if not name:
        return

    category = input("  Category: ").strip()
    spec = input("  Spec: ").strip()
    try:
        qty = int(input("  Quantity [1]: ").strip() or 1)
        plow = float(input("  Unit price low ($): ").strip() or 0)
        phigh = float(input("  Unit price high ($): ").strip() or 0)
    except ValueError:
        qty, plow, phigh = 1, 0, 0

    option = input("  Build option (a/b/meta/both) [both]: ").strip() or "both"
    notes = input("  Notes: ").strip()

    c = conn.cursor()
    c.execute(
        "INSERT INTO bom_items (name, category, spec, qty, unit_price_low, unit_price_high, build_option, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (name, category, spec, qty, plow, phigh, option, notes)
    )
    conn.commit()
    print(f"  Added: {name}")


def remove_item_interactive(conn):
    """Remove an item from the BOM."""
    print("\n  --- Remove BOM Item ---\n")
    q = input("  Search for item: ").strip()
    if not q:
        return

    c = conn.cursor()
    c.execute("SELECT id, name, spec, build_option FROM bom_items WHERE name LIKE ?", (f"%{q}%",))
    items = c.fetchall()
    if not items:
        print(f"  No items matching '{q}'")
        return

    for pid, name, spec, opt in items:
        print(f"    [{pid}] {name} ({spec}) — {opt}")

    try:
        pid = int(input("\n  Item ID to remove: ").strip())
        confirm = input("  Confirm delete? (y/n): ").strip().lower()
    except (ValueError, EOFError):
        return

    if confirm == "y":
        c.execute("DELETE FROM bom_items WHERE id = ?", (pid,))
        conn.commit()
        print("  Removed.")


def export_csv(conn):
    """Export BOM to CSV."""
    c = conn.cursor()
    c.execute("SELECT * FROM bom_items ORDER BY build_option, category, name")
    rows = c.fetchall()
    cols = [d[0] for d in c.description]

    out = get_db_path().with_suffix(".csv")
    with open(out, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(cols)
        writer.writerows(rows)
    print(f"\n  Exported {len(rows)} items to {out}")


def export_json(conn):
    """Export BOM to JSON."""
    c = conn.cursor()
    c.execute("SELECT * FROM bom_items ORDER BY build_option, category, name")
    cols = [d[0] for d in c.description]
    data = [dict(zip(cols, row)) for row in c.fetchall()]

    out = get_db_path().with_suffix(".json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n  Exported {len(data)} items to {out}")


# --- Shopping List ---

def shopping_list(conn, option=None):
    """Generate a shopping list of items not yet acquired."""
    c = conn.cursor()

    where = ["acquired = 0"]
    if option:
        if option == "a":
            where.append("build_option IN ('a', 'both')")
        elif option == "b":
            where.append("build_option IN ('b', 'both')")
        elif option == "full":
            where.append("build_option IN ('b', 'both', 'meta')")

    c.execute(
        f"SELECT name, category, spec, qty, unit_price_low, unit_price_high, notes "
        f"FROM bom_items WHERE {' AND '.join(where)} ORDER BY category, name"
    )
    items = c.fetchall()

    if not items:
        print("\n  All items acquired! Nothing left to buy.")
        return

    total_low = 0
    total_high = 0
    current_cat = None

    print(f"\n  SHOPPING LIST — {len(items)} items still needed")
    print(f"  {'=' * 60}")

    for name, cat, spec, qty, plow, phigh, notes in items:
        if cat != current_cat:
            current_cat = cat
            print(f"\n  [{cat.upper()}]")

        cost_low = plow * qty
        cost_high = phigh * qty
        total_low += cost_low
        total_high += cost_high
        note_str = f"  — {notes}" if notes else ""
        print(f"    [ ] {name} ({spec}) x{qty}  ${cost_low:.0f}-${cost_high:.0f}{note_str}")

    print(f"\n  {'─' * 60}")
    print(f"  Estimated remaining: ${total_low:,.0f} — ${total_high:,.0f}")


# --- Interactive ---

def interactive(conn):
    print("\n" + "=" * 55)
    print("  BOM CALCULATOR — DIY CNC Bill of Materials")
    print("=" * 55)

    while True:
        print("\n  [1] Show BOM (all)")
        print("  [2] Show BOM — Option A (prototype)")
        print("  [3] Show BOM — Option B (precision)")
        print("  [4] Show BOM — Metamaterial upgrade")
        print("  [5] Budget summary")
        print("  [6] Shopping list (what's left to buy)")
        print("  [7] Mark item as acquired")
        print("  [8] Add custom item")
        print("  [9] Remove item")
        print("  [e] Export (CSV + JSON)")
        print("  [q] Quit")

        choice = input("\n  > ").strip().lower()

        if choice == "1":
            show_bom(conn)
        elif choice == "2":
            show_bom(conn, option="a")
        elif choice == "3":
            show_bom(conn, option="b")
        elif choice == "4":
            show_bom(conn, option="meta")
        elif choice == "5":
            budget_summary(conn)
        elif choice == "6":
            opt = input("  Option (a/b/full/blank for all): ").strip().lower()
            shopping_list(conn, opt if opt else None)
        elif choice == "7":
            mark_acquired_interactive(conn)
        elif choice == "8":
            add_item_interactive(conn)
        elif choice == "9":
            remove_item_interactive(conn)
        elif choice == "e":
            export_csv(conn)
            export_json(conn)
        elif choice in ("q", "quit", "exit"):
            print("  Done.")
            break


def main():
    parser = argparse.ArgumentParser(description="DIY CNC BOM Calculator")
    sub = parser.add_subparsers(dest="command")

    p_show = sub.add_parser("show", help="Show BOM")
    p_show.add_argument("--option", choices=["a", "b", "meta", "full"], help="Build option filter")

    sub.add_parser("summary", help="Budget summary by option and category")

    p_shop = sub.add_parser("shopping", help="Shopping list (items not acquired)")
    p_shop.add_argument("--option", choices=["a", "b", "full"], help="Build option filter")

    sub.add_parser("export", help="Export BOM to CSV and JSON")
    sub.add_parser("acquired", help="Mark an item as acquired")

    args = parser.parse_args()

    conn = sqlite3.connect(get_db_path())
    init_db(conn)

    try:
        if args.command == "show":
            show_bom(conn, option=args.option)
        elif args.command == "summary":
            budget_summary(conn)
        elif args.command == "shopping":
            shopping_list(conn, option=getattr(args, "option", None))
        elif args.command == "export":
            export_csv(conn)
            export_json(conn)
        elif args.command == "acquired":
            mark_acquired_interactive(conn)
        else:
            interactive(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
