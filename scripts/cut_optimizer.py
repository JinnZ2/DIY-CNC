#!/usr/bin/env python3
"""
Cut List Optimizer — Minimize waste when cutting extrusion stock.

Given raw stock lengths and required cut pieces, calculates the optimal
cutting pattern to minimize waste. Uses a first-fit-decreasing bin packing
algorithm — simple, effective, no dependencies.

Usage:
    python cut_optimizer.py                        # Interactive mode
    python cut_optimizer.py optimize               # Run with CNC defaults
    python cut_optimizer.py optimize --stock 72    # Custom stock length (inches)
    python cut_optimizer.py optimize --kerf 0.125  # Account for blade kerf
"""

import argparse
import copy
import sys


# Default cut list from CNC-build.md Option B
DEFAULT_CUTS_INCHES = [
    # (length_inches, qty, label, profile)
    (72, 2, "X-axis base rails", "8080"),
    (52, 2, "Y-axis cross rails", "8080"),
    (30, 4, "Vertical posts", "8040"),
    (60, 4, "Gantry + bracing", "8040"),
    (40, 2, "Y-axis support rails", "8040"),
]

# Common stock lengths available
COMMON_STOCK_LENGTHS = {
    "8080": [48, 72, 96, 120, 144],  # inches
    "8040": [48, 72, 96, 120, 144],
    "generic": [48, 72, 96, 120, 144],
}


def expand_cuts(cut_list):
    """Expand (length, qty, label, profile) into individual cuts."""
    expanded = []
    for length, qty, label, profile in cut_list:
        for i in range(qty):
            expanded.append((length, f"{label} #{i + 1}", profile))
    return expanded


def optimize_cuts(stock_length, cuts, kerf=0.125):
    """
    First-fit-decreasing bin packing.

    Each 'bin' is a piece of stock. We try to fit cuts into existing
    stock pieces before opening a new one.

    Returns list of stock pieces, each containing its assigned cuts.
    """
    # Sort cuts longest first (greedy approach)
    sorted_cuts = sorted(cuts, key=lambda x: x[0], reverse=True)

    # Each stock piece: {"remaining": float, "cuts": [(length, label)], "stock_length": float}
    stocks = []

    for length, label, profile in sorted_cuts:
        if length > stock_length:
            print(f"  WARNING: '{label}' ({length}\") exceeds stock length ({stock_length}\")!")
            print(f"           You'll need longer stock or a splice joint.")
            # Still place it — user needs to know
            stocks.append({
                "remaining": 0,
                "cuts": [(length, label)],
                "stock_length": length,  # needs custom stock
                "profile": profile,
                "oversized": True,
            })
            continue

        # Try to fit in existing stock (first fit)
        placed = False
        for stock in stocks:
            if stock.get("profile") != profile:
                continue
            if stock["remaining"] >= length + kerf:
                stock["cuts"].append((length, label))
                stock["remaining"] -= (length + kerf)
                placed = True
                break

        if not placed:
            stocks.append({
                "remaining": stock_length - length - kerf,
                "cuts": [(length, label)],
                "stock_length": stock_length,
                "profile": profile,
                "oversized": False,
            })

    return stocks


def display_results(stocks, kerf):
    """Pretty-print the cutting plan."""
    profiles = sorted(set(s["profile"] for s in stocks))

    total_stock = 0
    total_used = 0
    total_waste = 0

    for profile in profiles:
        profile_stocks = [s for s in stocks if s["profile"] == profile]
        print(f"\n  PROFILE: {profile}")
        print(f"  {'─' * 60}")

        for i, stock in enumerate(profile_stocks, 1):
            sl = stock["stock_length"]
            total_stock += sl
            used = sum(c[0] for c in stock["cuts"])
            kerf_loss = kerf * len(stock["cuts"])
            waste = sl - used - kerf_loss
            total_used += used
            total_waste += max(0, waste)

            oversized = " ** OVERSIZED — needs special stock **" if stock.get("oversized") else ""
            print(f"\n    Stock #{i}: {sl}\" length{oversized}")
            print(f"    {'·' * 50}")

            # Visual bar
            bar_width = 50
            for length, label in stock["cuts"]:
                segment = int((length / sl) * bar_width)
                segment = max(segment, 1)
                print(f"    |{'█' * segment}| {length}\" — {label}")

            if waste > 0.1:
                waste_seg = int((waste / sl) * bar_width)
                waste_seg = max(waste_seg, 1)
                print(f"    |{'░' * waste_seg}| {waste:.2f}\" waste")

            print(f"    Used: {used:.2f}\" / {sl}\"  |  Waste: {max(0, waste):.2f}\"  "
                  f"|  Kerf loss: {kerf_loss:.3f}\"")

    print(f"\n  {'=' * 60}")
    print(f"  SUMMARY")
    print(f"  {'─' * 60}")

    stock_counts = {}
    for s in stocks:
        key = (s["profile"], s["stock_length"])
        stock_counts[key] = stock_counts.get(key, 0) + 1

    print(f"  Stock to purchase:")
    total_cost_estimate = 0
    for (profile, length), count in sorted(stock_counts.items()):
        # Rough cost estimate: ~$5-15/ft for 8080, ~$3-10/ft for 8040
        rate = 10 if "8080" in profile else 7  # $/ft midpoint
        cost = count * (length / 12) * rate
        total_cost_estimate += cost
        print(f"    {count}x {profile} @ {length}\"  (~${cost:.0f})")

    efficiency = (total_used / total_stock * 100) if total_stock > 0 else 0
    print(f"\n  Total stock:     {total_stock:.1f}\"")
    print(f"  Total used:      {total_used:.1f}\"")
    print(f"  Total waste:     {total_waste:.1f}\"")
    print(f"  Efficiency:      {efficiency:.1f}%")
    print(f"  Est. cost:       ~${total_cost_estimate:.0f} (rough)")


def try_all_stock_lengths(cuts, kerf, profiles=None):
    """Try different stock lengths and show which gives least waste."""
    if profiles is None:
        profiles = sorted(set(c[3] for c in cuts if len(c) > 3))
        if not profiles:
            profiles = ["generic"]

    print(f"\n  Comparing stock lengths for optimal purchase...\n")
    print(f"  {'Stock Length':<15s} {'# Pieces':<12s} {'Waste':<12s} {'Efficiency':<12s}")
    print(f"  {'─' * 51}")

    best = None
    best_waste = float("inf")

    for stock_len in [48, 72, 96, 120, 144]:
        expanded = expand_cuts(cuts)
        stocks = optimize_cuts(stock_len, expanded, kerf)
        total_stock = sum(s["stock_length"] for s in stocks)
        total_used = sum(sum(c[0] for c in s["cuts"]) for s in stocks)
        waste = total_stock - total_used
        eff = (total_used / total_stock * 100) if total_stock > 0 else 0
        n_pieces = len(stocks)

        marker = ""
        if waste < best_waste:
            best_waste = waste
            best = stock_len
            marker = " <-- best"

        print(f"  {stock_len}\"{'':>10s} {n_pieces:<12d} {waste:<12.1f} {eff:<12.1f}%{marker}")

    return best


# --- Interactive ---

def edit_cut_list(cuts):
    """Interactively edit the cut list."""
    while True:
        print(f"\n  Current cut list:")
        for i, (length, qty, label, profile) in enumerate(cuts):
            print(f"    [{i}] {qty}x {profile} @ {length}\" — {label}")

        print(f"\n  [a] Add cut  [r] Remove cut  [d] Done")
        choice = input("  > ").strip().lower()

        if choice == "a":
            try:
                profile = input("  Profile (8080/8040/other): ").strip() or "8040"
                length = float(input("  Length (inches): ").strip())
                qty = int(input("  Quantity [1]: ").strip() or 1)
                label = input("  Label: ").strip() or "Custom cut"
                cuts.append((length, qty, label, profile))
            except ValueError:
                print("  Invalid input.")
        elif choice == "r":
            try:
                idx = int(input("  Index to remove: ").strip())
                cuts.pop(idx)
            except (ValueError, IndexError):
                print("  Invalid index.")
        elif choice == "d":
            break

    return cuts


def interactive():
    print("\n" + "=" * 55)
    print("  CUT OPTIMIZER — Minimize Extrusion Waste")
    print("=" * 55)

    cuts = list(DEFAULT_CUTS_INCHES)
    kerf = 0.125  # 1/8" default saw kerf
    stock_length = 96  # 8ft default

    while True:
        print(f"\n  [1] Optimize with defaults (Option B build)")
        print(f"  [2] Edit cut list, then optimize")
        print(f"  [3] Compare all stock lengths")
        print(f"  [4] Change kerf width (current: {kerf}\")")
        print(f"  [5] Change default stock length (current: {stock_length}\")")
        print(f"  [q] Quit")

        choice = input("\n  > ").strip().lower()

        if choice == "1":
            expanded = expand_cuts(cuts)
            stocks = optimize_cuts(stock_length, expanded, kerf)
            display_results(stocks, kerf)
        elif choice == "2":
            cuts = edit_cut_list(list(cuts))
            expanded = expand_cuts(cuts)
            stocks = optimize_cuts(stock_length, expanded, kerf)
            display_results(stocks, kerf)
        elif choice == "3":
            try_all_stock_lengths(cuts, kerf)
        elif choice == "4":
            try:
                kerf = float(input(f"  Kerf width (inches) [{kerf}]: ").strip() or kerf)
            except ValueError:
                pass
        elif choice == "5":
            try:
                stock_length = float(input(f"  Stock length (inches) [{stock_length}]: ").strip() or stock_length)
            except ValueError:
                pass
        elif choice in ("q", "quit", "exit"):
            print("  Done.")
            break


def main():
    parser = argparse.ArgumentParser(description="DIY CNC Cut List Optimizer")
    sub = parser.add_subparsers(dest="command")

    p_opt = sub.add_parser("optimize", help="Optimize cuts with defaults")
    p_opt.add_argument("--stock", type=float, default=96, help="Stock length in inches (default: 96)")
    p_opt.add_argument("--kerf", type=float, default=0.125, help="Saw kerf in inches (default: 0.125)")

    p_cmp = sub.add_parser("compare", help="Compare all stock lengths")
    p_cmp.add_argument("--kerf", type=float, default=0.125, help="Saw kerf in inches")

    args = parser.parse_args()

    if args.command == "optimize":
        expanded = expand_cuts(DEFAULT_CUTS_INCHES)
        stocks = optimize_cuts(args.stock, expanded, args.kerf)
        display_results(stocks, args.kerf)
    elif args.command == "compare":
        try_all_stock_lengths(DEFAULT_CUTS_INCHES, args.kerf)
    else:
        interactive()


if __name__ == "__main__":
    main()
