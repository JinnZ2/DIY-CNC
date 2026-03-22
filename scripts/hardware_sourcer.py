#!/usr/bin/env python3
"""
Hardware Sourcer — Find CNC parts locally and from salvage.

Maintains a local SQLite database of parts, suppliers, salvage equivalents,
and substitution options. Helps you find what you need without internet.

Usage:
    python hardware_sourcer.py                     # Interactive mode
    python hardware_sourcer.py search "linear rail"
    python hardware_sourcer.py add-supplier
    python hardware_sourcer.py add-part
    python hardware_sourcer.py substitutes "HGR20"
    python hardware_sourcer.py export
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

DB_NAME = "hardware_sources.db"


def get_db_path():
    """Database lives next to this script."""
    return Path(__file__).parent / DB_NAME


def init_db(conn):
    """Create tables and seed with CNC-build defaults."""
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL DEFAULT 'store',
            location TEXT,
            notes TEXT,
            contact TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS parts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT,
            spec TEXT,
            use_for TEXT,
            est_price_low REAL,
            est_price_high REAL,
            notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS substitutes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_part TEXT NOT NULL,
            substitute TEXT NOT NULL,
            source_type TEXT,
            quality TEXT DEFAULT 'acceptable',
            notes TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS supplier_parts (
            supplier_id INTEGER,
            part_id INTEGER,
            price REAL,
            in_stock INTEGER DEFAULT 0,
            notes TEXT,
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (part_id) REFERENCES parts(id)
        )
    """)

    # Seed default parts from the CNC build docs if table is empty
    c.execute("SELECT COUNT(*) FROM parts")
    if c.fetchone()[0] == 0:
        _seed_defaults(c)

    conn.commit()


def _seed_defaults(cursor):
    """Seed the database with parts from CNC-build.md specs."""
    default_parts = [
        ("8080 Aluminum Extrusion 72in", "frame", "8080 x 72\"", "X-axis base rails", 40, 80, "Qty 2 needed"),
        ("8080 Aluminum Extrusion 52in", "frame", "8080 x 52\"", "Y-axis cross rails", 30, 60, "Qty 2 needed"),
        ("8040 Aluminum Extrusion 30in", "frame", "8040 x 30\"", "Vertical posts", 15, 35, "Qty 4 needed"),
        ("8040 Aluminum Extrusion 60in", "frame", "8040 x 60\"", "Gantry + bracing", 25, 50, "Qty 4 needed"),
        ("8040 Aluminum Extrusion 40in", "frame", "8040 x 40\"", "Y-axis support rails", 20, 40, "Qty 2 needed"),
        ("Cast Brackets + Gussets", "frame", "Standard", "Structural corner support", 2, 8, "20+ needed"),
        ("T-Slot Nuts/Bolts", "frame", "M8x20mm", "Frame and hardware assembly", 0.15, 0.50, "100+ needed"),
        ("Ball Screw 1605 x 2000mm", "motion", "1605 x 2000mm", "X-axis drive", 40, 120, None),
        ("Ball Screw 1605 x 1500mm", "motion", "1605 x 1500mm", "Y-axis drive", 35, 100, None),
        ("Ball Screw 1204 x 500mm", "motion", "1204 x 500mm", "Z-axis drive", 20, 60, None),
        ("Linear Guide HGR20 x 2000mm", "motion", "HGR20 x 2000mm", "X-axis precision", 30, 90, "With HGH20 blocks"),
        ("Linear Guide HGR20 x 1500mm", "motion", "HGR20 x 1500mm", "Y-axis precision", 25, 75, "With HGH20 blocks"),
        ("Linear Guide HGR15 x 500mm", "motion", "HGR15 x 500mm", "Z-axis precision", 15, 45, "With HGH15 blocks"),
        ("Pillow Blocks", "motion", "Standard", "All axes bearing support", 5, 20, "6 needed minimum"),
        ("Flexible Couplings", "motion", "Standard", "Motor-to-screw coupling", 3, 12, "3 needed"),
        ("NEMA 23 Stepper Motor", "electronics", "3Nm torque", "All axes drive", 15, 40, "Qty 3 needed"),
        ("DM542 Stepper Driver", "electronics", "DM542 or similar", "Motor driver", 15, 35, "Qty 3 needed"),
        ("Mesa 7i76e", "electronics", "7i76e", "LinuxCNC controller board", 200, 300, "Ethernet interface"),
        ("48V Power Supply", "electronics", "48V 10A", "Main power", 25, 60, None),
        ("Palm Router", "spindle", "DeWalt DWP611 or similar", "Initial spindle", 80, 130, "Upgradeable to ATC"),
        ("Router Clamp Mount", "spindle", "Adjustable", "Spindle mounting", 15, 40, None),
        ("BT30 Pneumatic Spindle", "toolchanger", "3HP 24000RPM", "ATC spindle upgrade", 400, 800, "Phase 2 upgrade"),
        ("Pneumatic ATC Unit", "toolchanger", "Umbrella-style", "Automatic tool changer", 300, 600, "8-position"),
        ("BT30 Tool Holders", "toolchanger", "BT30", "Tool holding", 15, 40, "8 needed for full carousel"),
        ("Cable Chain", "wiring", "25mm x 38mm", "Cable routing", 10, 30, None),
    ]

    default_subs = [
        ("HGR20 Linear Guide", "Drawer slides", "salvage", "prototype-only",
         "Fine for foam/wood cutting in Option A build"),
        ("Ball Screw 1605", "Threaded rod + brass nut", "hardware store", "prototype-only",
         "DIY lead screw for Option A; backlash is significant"),
        ("NEMA 23 Stepper", "NEMA 17 Stepper", "3d-printer-salvage", "acceptable",
         "Sufficient for light-duty Option A builds"),
        ("Mesa 7i76e", "Arduino + GRBL Shield", "electronics", "prototype-only",
         "Option A controller; not suitable for precision work"),
        ("8080 Aluminum Extrusion", "Steel angle iron", "junkyard", "acceptable",
         "Heavier but very cheap; needs drilling and welding"),
        ("8080 Aluminum Extrusion", "Bed frame rails", "salvage", "acceptable",
         "Surprisingly rigid; check for straightness"),
        ("DM542 Stepper Driver", "A4988 module", "3d-printer-salvage", "prototype-only",
         "Only for NEMA 17 / light loads"),
        ("Palm Router", "Rotary tool (Dremel)", "salvage", "prototype-only",
         "Very limited power but works for foam"),
        ("Pillow Blocks", "Skateboard bearings + printed mounts", "salvage", "prototype-only",
         "Low-cost linear bearing alternative"),
        ("48V Power Supply", "Server PSU (repurposed)", "salvage", "good",
         "Dell/HP server PSUs output 12V at high amps; need buck converter for 48V"),
        ("Cable Chain", "Split wire loom", "hardware store", "acceptable",
         "Cheaper but less protection"),
    ]

    for p in default_parts:
        cursor.execute(
            "INSERT INTO parts (name, category, spec, use_for, est_price_low, est_price_high, notes) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)", p
        )

    for s in default_subs:
        cursor.execute(
            "INSERT INTO substitutes (original_part, substitute, source_type, quality, notes) "
            "VALUES (?, ?, ?, ?, ?)", s
        )


# --- Search & Display ---

def search_parts(conn, query):
    """Search parts by name, category, or spec."""
    c = conn.cursor()
    q = f"%{query}%"
    c.execute(
        "SELECT id, name, category, spec, use_for, est_price_low, est_price_high, notes "
        "FROM parts WHERE name LIKE ? OR category LIKE ? OR spec LIKE ? OR use_for LIKE ?",
        (q, q, q, q)
    )
    results = c.fetchall()
    if not results:
        print(f"\n  No parts found matching '{query}'")
        return

    print(f"\n  Found {len(results)} part(s) matching '{query}':\n")
    for r in results:
        pid, name, cat, spec, use, plow, phigh, notes = r
        price_str = f"${plow:.0f}-${phigh:.0f}" if plow and phigh else "unknown"
        print(f"  [{pid}] {name}")
        print(f"      Category: {cat}  |  Spec: {spec}")
        print(f"      Use: {use}  |  Est. Price: {price_str}")
        if notes:
            print(f"      Notes: {notes}")
        # Show substitutes
        _show_subs_for(conn, name)
        # Show suppliers carrying this
        _show_suppliers_for(conn, pid)
        print()


def _show_subs_for(conn, part_name):
    c = conn.cursor()
    c.execute(
        "SELECT substitute, source_type, quality, notes FROM substitutes WHERE original_part LIKE ?",
        (f"%{part_name}%",)
    )
    subs = c.fetchall()
    if subs:
        print(f"      Substitutes:")
        for sub, src, qual, note in subs:
            print(f"        -> {sub} ({src}, {qual}){': ' + note if note else ''}")


def _show_suppliers_for(conn, part_id):
    c = conn.cursor()
    c.execute(
        "SELECT s.name, s.type, s.location, sp.price, sp.in_stock "
        "FROM supplier_parts sp JOIN suppliers s ON sp.supplier_id = s.id "
        "WHERE sp.part_id = ?", (part_id,)
    )
    suppliers = c.fetchall()
    if suppliers:
        print(f"      Local Suppliers:")
        for name, stype, loc, price, stock in suppliers:
            stock_str = "IN STOCK" if stock else "check availability"
            price_str = f"${price:.2f}" if price else "ask"
            print(f"        -> {name} ({stype}, {loc}) — {price_str}, {stock_str}")


def search_substitutes(conn, query):
    """Find substitution options for a part."""
    c = conn.cursor()
    q = f"%{query}%"
    c.execute(
        "SELECT original_part, substitute, source_type, quality, notes "
        "FROM substitutes WHERE original_part LIKE ? OR substitute LIKE ?",
        (q, q)
    )
    results = c.fetchall()
    if not results:
        print(f"\n  No substitutes found for '{query}'")
        return

    print(f"\n  Substitutes related to '{query}':\n")
    for orig, sub, src, qual, notes in results:
        print(f"  {orig}  ->  {sub}")
        print(f"    Source: {src}  |  Quality: {qual}")
        if notes:
            print(f"    Notes: {notes}")
        print()


def list_by_category(conn, category=None):
    """List all parts, optionally filtered by category."""
    c = conn.cursor()
    if category:
        c.execute("SELECT DISTINCT category FROM parts WHERE category LIKE ?", (f"%{category}%",))
    else:
        c.execute("SELECT DISTINCT category FROM parts ORDER BY category")
    cats = [row[0] for row in c.fetchall()]

    for cat in cats:
        c.execute(
            "SELECT name, spec, est_price_low, est_price_high FROM parts WHERE category = ? ORDER BY name",
            (cat,)
        )
        parts = c.fetchall()
        print(f"\n  [{cat.upper()}]")
        for name, spec, plow, phigh in parts:
            price = f"${plow:.0f}-${phigh:.0f}" if plow and phigh else ""
            print(f"    {name:<40s} {spec:<20s} {price}")


# --- Add data ---

def add_supplier_interactive(conn):
    """Interactively add a local supplier."""
    print("\n  --- Add Local Supplier ---\n")
    name = input("  Supplier name: ").strip()
    if not name:
        print("  Cancelled.")
        return
    stype = input("  Type (store/junkyard/salvage/online/other) [store]: ").strip() or "store"
    location = input("  Location/address: ").strip()
    contact = input("  Contact info (phone/email): ").strip()
    notes = input("  Notes: ").strip()

    c = conn.cursor()
    c.execute(
        "INSERT INTO suppliers (name, type, location, contact, notes) VALUES (?, ?, ?, ?, ?)",
        (name, stype, location, contact, notes)
    )
    conn.commit()
    print(f"\n  Added supplier: {name} (ID: {c.lastrowid})")


def add_part_interactive(conn):
    """Interactively add a custom part."""
    print("\n  --- Add Part ---\n")
    name = input("  Part name: ").strip()
    if not name:
        print("  Cancelled.")
        return
    category = input("  Category (frame/motion/electronics/spindle/toolchanger/wiring/other): ").strip()
    spec = input("  Spec/size: ").strip()
    use = input("  Used for: ").strip()
    try:
        plow = float(input("  Est. price low ($): ").strip() or 0)
        phigh = float(input("  Est. price high ($): ").strip() or 0)
    except ValueError:
        plow, phigh = 0, 0
    notes = input("  Notes: ").strip()

    c = conn.cursor()
    c.execute(
        "INSERT INTO parts (name, category, spec, use_for, est_price_low, est_price_high, notes) "
        "VALUES (?, ?, ?, ?, ?, ?, ?)",
        (name, category, spec, use, plow, phigh, notes)
    )
    conn.commit()
    print(f"\n  Added part: {name} (ID: {c.lastrowid})")


def add_substitute_interactive(conn):
    """Interactively add a substitution option."""
    print("\n  --- Add Substitute ---\n")
    original = input("  Original part name: ").strip()
    if not original:
        print("  Cancelled.")
        return
    sub = input("  Substitute: ").strip()
    source = input("  Source type (salvage/junkyard/hardware store/3d-printer-salvage/other): ").strip()
    quality = input("  Quality (good/acceptable/prototype-only) [acceptable]: ").strip() or "acceptable"
    notes = input("  Notes: ").strip()

    c = conn.cursor()
    c.execute(
        "INSERT INTO substitutes (original_part, substitute, source_type, quality, notes) "
        "VALUES (?, ?, ?, ?, ?)",
        (original, sub, source, quality, notes)
    )
    conn.commit()
    print(f"\n  Added substitute: {original} -> {sub}")


def link_supplier_part(conn):
    """Link a supplier to a part they carry."""
    print("\n  --- Link Supplier to Part ---\n")

    c = conn.cursor()
    c.execute("SELECT id, name, type, location FROM suppliers ORDER BY name")
    suppliers = c.fetchall()
    if not suppliers:
        print("  No suppliers in database. Add one first.")
        return

    print("  Suppliers:")
    for sid, name, stype, loc in suppliers:
        print(f"    [{sid}] {name} ({stype}, {loc})")

    try:
        sid = int(input("\n  Supplier ID: ").strip())
    except ValueError:
        print("  Cancelled.")
        return

    search = input("  Search for part: ").strip()
    c.execute("SELECT id, name, spec FROM parts WHERE name LIKE ? OR spec LIKE ?",
              (f"%{search}%", f"%{search}%"))
    parts = c.fetchall()
    if not parts:
        print(f"  No parts matching '{search}'")
        return

    for pid, name, spec in parts:
        print(f"    [{pid}] {name} — {spec}")

    try:
        pid = int(input("\n  Part ID: ").strip())
        price = float(input("  Price at this supplier ($): ").strip() or 0)
        stock = input("  In stock? (y/n) [n]: ").strip().lower() == "y"
    except ValueError:
        print("  Cancelled.")
        return

    c.execute(
        "INSERT INTO supplier_parts (supplier_id, part_id, price, in_stock) VALUES (?, ?, ?, ?)",
        (sid, pid, price, 1 if stock else 0)
    )
    conn.commit()
    print("  Linked.")


def export_db(conn):
    """Export entire database as JSON for portability."""
    c = conn.cursor()
    data = {}

    for table in ("suppliers", "parts", "substitutes", "supplier_parts"):
        c.execute(f"SELECT * FROM {table}")
        cols = [d[0] for d in c.description]
        data[table] = [dict(zip(cols, row)) for row in c.fetchall()]

    out = get_db_path().with_suffix(".json")
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
    print(f"\n  Exported to {out}")


# --- Interactive Mode ---

def interactive(conn):
    """Main interactive menu."""
    print("\n" + "=" * 55)
    print("  HARDWARE SOURCER — DIY CNC Parts Finder")
    print("=" * 55)

    while True:
        print("\n  [1] Search parts")
        print("  [2] Find substitutes / salvage options")
        print("  [3] Browse by category")
        print("  [4] Add local supplier")
        print("  [5] Add custom part")
        print("  [6] Add substitute")
        print("  [7] Link supplier to part")
        print("  [8] Export database (JSON)")
        print("  [q] Quit")

        choice = input("\n  > ").strip().lower()

        if choice == "1":
            q = input("  Search: ").strip()
            if q:
                search_parts(conn, q)
        elif choice == "2":
            q = input("  Part name: ").strip()
            if q:
                search_substitutes(conn, q)
        elif choice == "3":
            cat = input("  Category (blank for all): ").strip()
            list_by_category(conn, cat if cat else None)
        elif choice == "4":
            add_supplier_interactive(conn)
        elif choice == "5":
            add_part_interactive(conn)
        elif choice == "6":
            add_substitute_interactive(conn)
        elif choice == "7":
            link_supplier_part(conn)
        elif choice == "8":
            export_db(conn)
        elif choice in ("q", "quit", "exit"):
            print("  Done.")
            break


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="DIY CNC Hardware Sourcer")
    sub = parser.add_subparsers(dest="command")

    p_search = sub.add_parser("search", help="Search for parts")
    p_search.add_argument("query", help="Search term")

    p_subs = sub.add_parser("substitutes", help="Find substitutes for a part")
    p_subs.add_argument("query", help="Part name")

    p_list = sub.add_parser("list", help="List parts by category")
    p_list.add_argument("category", nargs="?", help="Category filter")

    sub.add_parser("add-supplier", help="Add a local supplier")
    sub.add_parser("add-part", help="Add a custom part")
    sub.add_parser("add-substitute", help="Add a substitution option")
    sub.add_parser("link", help="Link a supplier to a part")
    sub.add_parser("export", help="Export database as JSON")

    args = parser.parse_args()

    conn = sqlite3.connect(get_db_path())
    init_db(conn)

    try:
        if args.command == "search":
            search_parts(conn, args.query)
        elif args.command == "substitutes":
            search_substitutes(conn, args.query)
        elif args.command == "list":
            list_by_category(conn, args.category)
        elif args.command == "add-supplier":
            add_supplier_interactive(conn)
        elif args.command == "add-part":
            add_part_interactive(conn)
        elif args.command == "add-substitute":
            add_substitute_interactive(conn)
        elif args.command == "link":
            link_supplier_part(conn)
        elif args.command == "export":
            export_db(conn)
        else:
            interactive(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
