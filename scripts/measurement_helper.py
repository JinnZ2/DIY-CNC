#!/usr/bin/env python3
"""
Measurement Helper — Precision measuring with imprecise tools.

Guides you through measuring critical CNC dimensions using whatever
tools you have on hand: tape measure, ruler, calipers, or even
a piece of string and a reference object.

Includes error compensation, squareness checks, and leveling calculations.

Usage:
    python measurement_helper.py                  # Interactive mode
    python measurement_helper.py squareness
    python measurement_helper.py level
    python measurement_helper.py convert 25.4mm
    python measurement_helper.py repeated
    python measurement_helper.py calibrate
"""

import argparse
import math
import statistics
import sys


# --- Unit Conversion ---

UNIT_TO_MM = {
    "mm": 1.0,
    "cm": 10.0,
    "m": 1000.0,
    "in": 25.4,
    "inch": 25.4,
    "inches": 25.4,
    "ft": 304.8,
    "feet": 304.8,
    "thou": 0.0254,
    "mil": 0.0254,
}


def parse_measurement(text):
    """Parse a measurement string like '25.4mm' or '1.5 in' into mm."""
    text = text.strip().lower()
    for unit, factor in sorted(UNIT_TO_MM.items(), key=lambda x: -len(x[0])):
        if text.endswith(unit):
            try:
                val = float(text[:-len(unit)].strip())
                return val * factor, unit
            except ValueError:
                pass
    # Try bare number (assume mm)
    try:
        return float(text), "mm"
    except ValueError:
        return None, None


def convert_measurement(value_mm, to_unit):
    """Convert mm to target unit."""
    factor = UNIT_TO_MM.get(to_unit, 1.0)
    return value_mm / factor


def format_all_units(mm_val):
    """Show a measurement in all common units."""
    lines = []
    lines.append(f"    {mm_val:.3f} mm")
    lines.append(f"    {mm_val / 10:.4f} cm")
    lines.append(f"    {mm_val / 25.4:.4f} in")
    lines.append(f"    {mm_val / 25.4 * 1000:.1f} thou")
    if mm_val >= 304.8:
        lines.append(f"    {mm_val / 304.8:.3f} ft")
    return "\n".join(lines)


def convert_interactive():
    """Convert between units."""
    print("\n  --- Unit Converter ---")
    print("  Enter a measurement with unit (e.g., '25.4mm', '1 in', '3.5 ft')")
    print("  Supported: mm, cm, m, in/inch, ft/feet, thou/mil\n")

    val = input("  Measurement: ").strip()
    mm_val, unit = parse_measurement(val)
    if mm_val is None:
        print("  Could not parse. Use format like '25.4mm' or '1.5 in'")
        return
    print(f"\n  {val} =\n{format_all_units(mm_val)}")


# --- Repeated Measurement (statistical precision) ---

def repeated_measurement():
    """Take multiple measurements and compute statistics for precision."""
    print("\n  --- Repeated Measurement (Improve Precision) ---")
    print("  Take the same measurement multiple times.")
    print("  More readings = better accuracy. Aim for 5-10.\n")

    unit = input("  Unit (mm/in/cm) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    readings = []
    print("  Enter readings one at a time. Type 'done' when finished.\n")

    while True:
        r = input(f"  Reading #{len(readings) + 1} ({unit}): ").strip()
        if r.lower() in ("done", "d", ""):
            if len(readings) < 2:
                print("  Need at least 2 readings.")
                continue
            break
        try:
            readings.append(float(r))
        except ValueError:
            print("  Enter a number.")

    mm_readings = [r * factor for r in readings]
    mean = statistics.mean(mm_readings)
    stdev = statistics.stdev(mm_readings) if len(mm_readings) > 1 else 0
    median = statistics.median(mm_readings)
    spread = max(mm_readings) - min(mm_readings)

    print(f"\n  Results ({len(readings)} readings):")
    print(f"  ──────────────────────────────")
    print(f"  Mean:      {mean:.3f} mm  ({mean / factor:.3f} {unit})")
    print(f"  Median:    {median:.3f} mm  ({median / factor:.3f} {unit})")
    print(f"  Std Dev:   {stdev:.3f} mm  ({stdev / factor:.3f} {unit})")
    print(f"  Spread:    {spread:.3f} mm  ({spread / factor:.3f} {unit})")
    print(f"  95% conf:  ±{1.96 * stdev / math.sqrt(len(readings)):.3f} mm")

    if stdev > 0.5:
        print("\n  ⚠ High variation — try clamping your workpiece or measuring point.")
    elif stdev > 0.1:
        print("\n  Decent consistency. Your effective precision is ~±{:.2f}mm.".format(stdev))
    else:
        print("\n  Excellent consistency.")


# --- Squareness Check ---

def squareness_check():
    """Check if a frame is square using diagonal measurements."""
    print("\n  --- Squareness Check ---")
    print("  Measure the two diagonals of your rectangular frame.")
    print("  A perfectly square frame has equal diagonals.\n")

    unit = input("  Unit (mm/in/ft) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    try:
        d1 = float(input(f"  Diagonal 1 ({unit}): ").strip()) * factor
        d2 = float(input(f"  Diagonal 2 ({unit}): ").strip()) * factor
        width = float(input(f"  Frame width ({unit}): ").strip()) * factor
        length = float(input(f"  Frame length ({unit}): ").strip()) * factor
    except ValueError:
        print("  Invalid input.")
        return

    diff = abs(d1 - d2)
    expected = math.sqrt(width ** 2 + length ** 2)
    avg_diag = (d1 + d2) / 2

    # Calculate how far out of square (offset at one corner)
    # Using the relationship between diagonal difference and corner offset
    if length > 0:
        offset = (diff * length) / (2 * expected) if expected > 0 else 0
    else:
        offset = 0

    print(f"\n  Results:")
    print(f"  ──────────────────────────────")
    print(f"  Diagonal 1:     {d1:.2f} mm")
    print(f"  Diagonal 2:     {d2:.2f} mm")
    print(f"  Difference:     {diff:.2f} mm ({diff / factor:.3f} {unit})")
    print(f"  Expected diag:  {expected:.2f} mm")
    print(f"  Corner offset:  ~{offset:.2f} mm")

    if diff < 0.5:
        print("\n  Excellent — frame is very square.")
    elif diff < 2.0:
        print(f"\n  Good — minor adjustment needed. Tap the long-diagonal corners inward ~{offset:.1f}mm.")
    else:
        print(f"\n  Needs work — {offset:.1f}mm offset. Loosen bolts, use a bar clamp across the long diagonal, retighten.")


# --- Level Check ---

def level_check():
    """Calculate shimming needed for leveling using reference measurements."""
    print("\n  --- Level / Flatness Check ---")
    print("  Measure the height at multiple points along your surface.")
    print("  Use a reference surface + gauge, or measure from the floor.\n")

    unit = input("  Unit (mm/in) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    points = []
    print("  Enter height readings at different positions.")
    print("  Label each point (e.g., 'front-left'). Type 'done' when finished.\n")

    while True:
        label = input("  Point label (or 'done'): ").strip()
        if label.lower() in ("done", "d", ""):
            if len(points) < 3:
                print("  Need at least 3 points for useful analysis.")
                continue
            break
        try:
            height = float(input(f"    Height at '{label}' ({unit}): ").strip()) * factor
            points.append((label, height))
        except ValueError:
            print("    Enter a number.")

    heights = [h for _, h in points]
    min_h = min(heights)
    max_h = max(heights)
    mean_h = statistics.mean(heights)
    ref_point = min(points, key=lambda x: x[1])

    print(f"\n  Leveling Analysis:")
    print(f"  ──────────────────────────────")
    print(f"  Reference (lowest): {ref_point[0]} at {ref_point[1]:.2f}mm")
    print(f"  Total variation:    {max_h - min_h:.2f}mm ({(max_h - min_h) / factor:.3f} {unit})")
    print(f"\n  Shim Requirements (relative to {ref_point[0]}):")

    for label, h in points:
        shim = h - min_h
        if shim > 0.01:
            print(f"    {label}: needs {shim:.2f}mm ({shim / factor:.3f} {unit}) shim REMOVED or surface lowered")
        else:
            print(f"    {label}: reference level (no shim)")

    if max_h - min_h < 0.1:
        print("\n  Surface is very flat — within 0.1mm.")
    elif max_h - min_h < 0.5:
        print("\n  Acceptable for CNC work. Consider shimming for best results.")
    else:
        print(f"\n  {max_h - min_h:.1f}mm variation is significant. Shim or machine the surface flat.")


# --- Tool Calibration ---

def calibrate_tool():
    """Calibrate a measuring tool against a known reference."""
    print("\n  --- Tool Calibration ---")
    print("  Compare your measuring tool against a known reference dimension.")
    print("  This gives you a correction factor for all future measurements.\n")

    unit = input("  Unit (mm/in) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    try:
        known = float(input(f"  Known reference dimension ({unit}): ").strip()) * factor
        print(f"  Now measure that same dimension with your tool (3 times):")
        readings = []
        for i in range(3):
            r = float(input(f"    Reading {i + 1} ({unit}): ").strip()) * factor
            readings.append(r)
    except ValueError:
        print("  Invalid input.")
        return

    measured_avg = statistics.mean(readings)
    error = measured_avg - known
    correction = known / measured_avg if measured_avg != 0 else 1.0

    print(f"\n  Calibration Results:")
    print(f"  ──────────────────────────────")
    print(f"  Known value:      {known:.3f} mm")
    print(f"  Your average:     {measured_avg:.3f} mm")
    print(f"  Error:            {error:+.3f} mm ({error / known * 100:+.2f}%)")
    print(f"  Correction factor: {correction:.6f}")
    print(f"\n  To use: multiply your readings by {correction:.4f}")
    print(f"  Example: if you measure 100{unit}, actual is {100 * correction:.2f}{unit}")

    if abs(error / known) < 0.001:
        print("\n  Your tool is well-calibrated (<0.1% error).")
    elif abs(error / known) < 0.005:
        print("\n  Minor error. Apply correction factor for precision work.")
    else:
        print("\n  Significant error. Always apply correction, or consider a better tool for critical dimensions.")


# --- Angle Measurement ---

def angle_from_sides():
    """Calculate angles from side measurements (no protractor needed)."""
    print("\n  --- Angle from Side Measurements ---")
    print("  Measure three sides of a triangle to find angles.")
    print("  Useful for checking angles without a protractor.\n")

    unit = input("  Unit (mm/in) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    try:
        a = float(input(f"  Side A ({unit}): ").strip()) * factor
        b = float(input(f"  Side B ({unit}): ").strip()) * factor
        c = float(input(f"  Side C (opposite the angle you want) ({unit}): ").strip()) * factor
    except ValueError:
        print("  Invalid input.")
        return

    # Law of cosines: c² = a² + b² - 2ab*cos(C)
    try:
        cos_C = (a ** 2 + b ** 2 - c ** 2) / (2 * a * b)
        cos_C = max(-1, min(1, cos_C))  # clamp for floating point
        angle_C = math.degrees(math.acos(cos_C))
    except (ValueError, ZeroDivisionError):
        print("  These sides don't form a valid triangle.")
        return

    print(f"\n  Angle opposite side C: {angle_C:.2f}°")
    print(f"  Deviation from 90°:   {angle_C - 90:+.2f}°")

    if abs(angle_C - 90) < 0.5:
        print("  Very close to 90° — good for frame corners.")
    elif abs(angle_C - 90) < 2:
        print("  Slightly off square — minor adjustment needed.")
    else:
        print("  Significantly off 90° — check your frame alignment.")


# --- 3-4-5 Method ---

def three_four_five():
    """Guide for using the 3-4-5 method to check right angles."""
    print("\n  --- 3-4-5 Right Angle Check ---")
    print("  The classic builder's method for checking 90° angles.\n")

    unit = input("  Unit (mm/in/ft) [mm]: ").strip() or "mm"
    factor = UNIT_TO_MM.get(unit, 1.0)

    print("\n  Choose your scale (the '3' side length):")
    try:
        base = float(input(f"  '3' side ({unit}): ").strip())
    except ValueError:
        print("  Invalid input.")
        return

    side_4 = base * 4 / 3
    side_5 = base * 5 / 3

    print(f"\n  For a perfect 90° angle:")
    print(f"  ──────────────────────────────")
    print(f"  Side 1:   {base:.2f} {unit}")
    print(f"  Side 2:   {side_4:.2f} {unit}")
    print(f"  Diagonal: {side_5:.2f} {unit}")
    print(f"\n  Mark {base:.2f} along one edge, {side_4:.2f} along the other.")
    print(f"  The diagonal between those marks should be exactly {side_5:.2f}.")
    print(f"\n  Now measure your actual diagonal:")

    try:
        actual = float(input(f"  Measured diagonal ({unit}): ").strip())
    except ValueError:
        return

    diff = actual - side_5
    diff_mm = diff * factor
    print(f"\n  Diagonal error: {diff:+.3f} {unit} ({diff_mm:+.3f} mm)")

    if abs(diff_mm) < 0.5:
        print("  Excellent — angle is very close to 90°.")
    elif abs(diff_mm) < 2:
        print("  Minor deviation. Adjust and remeasure.")
    else:
        print("  Needs significant correction.")


# --- Interactive Mode ---

def interactive():
    """Main interactive menu."""
    print("\n" + "=" * 55)
    print("  MEASUREMENT HELPER — Precision with Simple Tools")
    print("=" * 55)

    while True:
        print("\n  [1] Unit converter")
        print("  [2] Repeated measurement (statistical precision)")
        print("  [3] Squareness check (diagonal method)")
        print("  [4] Level / flatness check")
        print("  [5] Calibrate your measuring tool")
        print("  [6] Angle from side measurements")
        print("  [7] 3-4-5 right angle check")
        print("  [q] Quit")

        choice = input("\n  > ").strip().lower()

        if choice == "1":
            convert_interactive()
        elif choice == "2":
            repeated_measurement()
        elif choice == "3":
            squareness_check()
        elif choice == "4":
            level_check()
        elif choice == "5":
            calibrate_tool()
        elif choice == "6":
            angle_from_sides()
        elif choice == "7":
            three_four_five()
        elif choice in ("q", "quit", "exit"):
            print("  Done.")
            break


# --- CLI ---

def main():
    parser = argparse.ArgumentParser(description="DIY CNC Measurement Helper")
    sub = parser.add_subparsers(dest="command")

    p_conv = sub.add_parser("convert", help="Convert a measurement between units")
    p_conv.add_argument("value", help="Value with unit, e.g. '25.4mm'")

    sub.add_parser("squareness", help="Check frame squareness via diagonals")
    sub.add_parser("level", help="Check surface level / flatness")
    sub.add_parser("repeated", help="Statistical precision from repeated measurements")
    sub.add_parser("calibrate", help="Calibrate a measuring tool")
    sub.add_parser("angle", help="Calculate angle from side measurements")
    sub.add_parser("345", help="3-4-5 right angle check")

    args = parser.parse_args()

    if args.command == "convert":
        mm_val, unit = parse_measurement(args.value)
        if mm_val is None:
            print("  Could not parse. Use format like '25.4mm' or '1.5in'")
        else:
            print(f"\n  {args.value} =\n{format_all_units(mm_val)}")
    elif args.command == "squareness":
        squareness_check()
    elif args.command == "level":
        level_check()
    elif args.command == "repeated":
        repeated_measurement()
    elif args.command == "calibrate":
        calibrate_tool()
    elif args.command == "angle":
        angle_from_sides()
    elif args.command == "345":
        three_four_five()
    else:
        interactive()


if __name__ == "__main__":
    main()
