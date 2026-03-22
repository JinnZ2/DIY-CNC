#!/usr/bin/env python3
"""
LinuxCNC Config Generator — Generate starter INI and HAL files.

Creates LinuxCNC configuration files based on your specific motor, driver,
and board choices. Outputs ready-to-use configs that you can drop into
your LinuxCNC installation.

Usage:
    python linuxcnc_config.py                  # Interactive mode
    python linuxcnc_config.py generate          # Generate with defaults
    python linuxcnc_config.py generate --dir .  # Output to current dir
"""

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

# --- Default Machine Config (from CNC-build.md Option B) ---

DEFAULT_CONFIG = {
    "machine_name": "DIY-CNC-BioDesign",
    "axes": 3,  # XYZ

    # Geometry (inches converted to mm for LinuxCNC)
    "x_travel_mm": 1524.0,   # 60"
    "y_travel_mm": 1016.0,   # 40"
    "z_travel_mm": 152.4,    # 6"

    # Ball screws
    "x_screw_pitch_mm": 5.0,   # 1605 = 5mm pitch
    "y_screw_pitch_mm": 5.0,   # 1605
    "z_screw_pitch_mm": 4.0,   # 1204 = 4mm pitch

    # Stepper motors (NEMA 23, 200 steps/rev)
    "steps_per_rev": 200,
    "microstepping": 8,  # DM542 typical setting

    # Driver: DM542
    "driver_type": "DM542",

    # Controller: Mesa 7i76e
    "controller": "mesa_7i76e",

    # Speeds (conservative defaults)
    "x_max_vel_mm_s": 50.0,
    "y_max_vel_mm_s": 50.0,
    "z_max_vel_mm_s": 25.0,
    "x_max_accel_mm_s2": 500.0,
    "y_max_accel_mm_s2": 500.0,
    "z_max_accel_mm_s2": 250.0,

    # Homing
    "home_sequence": "z_first",  # Z homes first (safety)

    # Spindle
    "spindle_type": "router",  # router or vfd
    "spindle_max_rpm": 27000,

    # I/O
    "has_home_switches": True,
    "has_limit_switches": True,
    "has_estop": True,
    "has_probe": False,

    # Units
    "linear_units": "mm",
}


def calc_scale(screw_pitch_mm, steps_per_rev, microstepping):
    """Calculate axis scale (steps per mm)."""
    steps_per_turn = steps_per_rev * microstepping
    return steps_per_turn / screw_pitch_mm


def generate_ini(config, output_dir):
    """Generate the .ini configuration file."""
    x_scale = calc_scale(config["x_screw_pitch_mm"], config["steps_per_rev"], config["microstepping"])
    y_scale = calc_scale(config["y_screw_pitch_mm"], config["steps_per_rev"], config["microstepping"])
    z_scale = calc_scale(config["z_screw_pitch_mm"], config["steps_per_rev"], config["microstepping"])

    name = config["machine_name"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    ini = f"""\
# LinuxCNC Configuration — {name}
# Generated: {timestamp}
# Generator: DIY-CNC linuxcnc_config.py
#
# Review all values before running. These are starting points
# based on the DIY-CNC build specifications.

[EMC]
VERSION = 1.1
MACHINE = {name}
DEBUG = 0

[DISPLAY]
DISPLAY = axis
TITLE = {name}
CYCLE_TIME = 0.100
POSITION_OFFSET = RELATIVE
POSITION_FEEDBACK = ACTUAL
MAX_FEED_OVERRIDE = 1.5
MAX_SPINDLE_OVERRIDE = 1.2
MIN_SPINDLE_OVERRIDE = 0.5
DEFAULT_LINEAR_VELOCITY = 25.0
MAX_LINEAR_VELOCITY = {max(config["x_max_vel_mm_s"], config["y_max_vel_mm_s"]):.1f}
MIN_LINEAR_VELOCITY = 1.0
DEFAULT_ANGULAR_VELOCITY = 10.0
EDITOR = gedit
GEOMETRY = AXYZ
INTRO_GRAPHIC = linuxcnc.gif
INTRO_TIME = 3

[FILTER]
PROGRAM_EXTENSION = .py Python Script
PROGRAM_EXTENSION = .nc G-Code
py = python3

[RS274NGC]
PARAMETER_FILE = {name}.var
SUBROUTINE_PATH = ./subroutines
RS274NGC_STARTUP_CODE = G21 G40 G49 G54 G80 G90 G94

[EMCMOT]
EMCMOT = motmod
COMM_TIMEOUT = 1.0
BASE_PERIOD = 0
SERVO_PERIOD = 1000000

[EMCIO]
EMCIO = io
CYCLE_TIME = 0.100
TOOL_TABLE = tool.tbl
TOOL_CHANGE_POSITION = 0 0 50

[TASK]
TASK = milltask
CYCLE_TIME = 0.001

[HAL]
HALFILE = {name}.hal
POSTGUI_HALFILE = postgui.hal

[TRAJ]
COORDINATES = X Y Z
LINEAR_UNITS = {config["linear_units"]}
ANGULAR_UNITS = degree
MAX_LINEAR_VELOCITY = {max(config["x_max_vel_mm_s"], config["y_max_vel_mm_s"]):.1f}
DEFAULT_LINEAR_VELOCITY = 25.0
MAX_LINEAR_ACCELERATION = {max(config["x_max_accel_mm_s2"], config["y_max_accel_mm_s2"]):.1f}
NO_FORCE_HOMING = 1

# ─── X AXIS ───────────────────────────────────────────
[AXIS_X]
MIN_LIMIT = -1.0
MAX_LIMIT = {config["x_travel_mm"]:.1f}
MAX_VELOCITY = {config["x_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["x_max_accel_mm_s2"]:.1f}

[JOINT_0]
TYPE = LINEAR
MIN_LIMIT = -1.0
MAX_LIMIT = {config["x_travel_mm"]:.1f}
MAX_VELOCITY = {config["x_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["x_max_accel_mm_s2"]:.1f}
SCALE = {x_scale:.4f}
FERROR = 5.0
MIN_FERROR = 1.0
HOME = 0.0
HOME_OFFSET = -5.0
HOME_SEARCH_VEL = -10.0
HOME_LATCH_VEL = 2.0
HOME_SEQUENCE = 1
HOME_USE_INDEX = NO
STEPGEN_MAXACCEL = {config["x_max_accel_mm_s2"] * 1.25:.1f}
STEPGEN_MAXVEL = {config["x_max_vel_mm_s"] * 1.25:.1f}

# ─── Y AXIS ───────────────────────────────────────────
[AXIS_Y]
MIN_LIMIT = -1.0
MAX_LIMIT = {config["y_travel_mm"]:.1f}
MAX_VELOCITY = {config["y_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["y_max_accel_mm_s2"]:.1f}

[JOINT_1]
TYPE = LINEAR
MIN_LIMIT = -1.0
MAX_LIMIT = {config["y_travel_mm"]:.1f}
MAX_VELOCITY = {config["y_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["y_max_accel_mm_s2"]:.1f}
SCALE = {y_scale:.4f}
FERROR = 5.0
MIN_FERROR = 1.0
HOME = 0.0
HOME_OFFSET = -5.0
HOME_SEARCH_VEL = -10.0
HOME_LATCH_VEL = 2.0
HOME_SEQUENCE = 1
HOME_USE_INDEX = NO
STEPGEN_MAXACCEL = {config["y_max_accel_mm_s2"] * 1.25:.1f}
STEPGEN_MAXVEL = {config["y_max_vel_mm_s"] * 1.25:.1f}

# ─── Z AXIS ───────────────────────────────────────────
[AXIS_Z]
MIN_LIMIT = -{config["z_travel_mm"]:.1f}
MAX_LIMIT = 1.0
MAX_VELOCITY = {config["z_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["z_max_accel_mm_s2"]:.1f}

[JOINT_2]
TYPE = LINEAR
MIN_LIMIT = -{config["z_travel_mm"]:.1f}
MAX_LIMIT = 1.0
MAX_VELOCITY = {config["z_max_vel_mm_s"]:.1f}
MAX_ACCELERATION = {config["z_max_accel_mm_s2"]:.1f}
SCALE = {z_scale:.4f}
FERROR = 2.5
MIN_FERROR = 0.5
HOME = 0.0
HOME_OFFSET = 5.0
HOME_SEARCH_VEL = 5.0
HOME_LATCH_VEL = -1.0
HOME_SEQUENCE = 0
HOME_USE_INDEX = NO
STEPGEN_MAXACCEL = {config["z_max_accel_mm_s2"] * 1.25:.1f}
STEPGEN_MAXVEL = {config["z_max_vel_mm_s"] * 1.25:.1f}

# ─── SPINDLE ──────────────────────────────────────────
[SPINDLE_0]
MAX_FORWARD_VELOCITY = {config["spindle_max_rpm"]:.0f}
MIN_FORWARD_VELOCITY = 5000
"""

    filepath = Path(output_dir) / f"{name}.ini"
    with open(filepath, "w") as f:
        f.write(ini)
    return filepath


def generate_hal(config, output_dir):
    """Generate the .hal configuration file for Mesa 7i76e."""
    name = config["machine_name"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    is_mesa = config["controller"] == "mesa_7i76e"

    if is_mesa:
        hal = f"""\
# HAL Configuration — {name}
# Generated: {timestamp}
# Controller: Mesa 7i76e
#
# IMPORTANT: Verify pin assignments match your physical wiring.

# ─── Load RT modules ─────────────────────────────────
loadrt [KINS]KINEMATICS
loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=3
loadrt hostmot2
loadrt hm2_eth board_ip="192.168.1.121" config="firmware=hm2/7i76e/7i76e_7i76x1D.bit num_encoders=0 num_pwmgens=0 num_stepgens=3"

# ─── Thread connections ──────────────────────────────
addf hm2_7i76e.0.read servo-thread
addf motion-command-handler servo-thread
addf motion-controller servo-thread
addf hm2_7i76e.0.write servo-thread

# ─── X AXIS (Joint 0) ────────────────────────────────
setp hm2_7i76e.0.stepgen.00.dirsetup        5000
setp hm2_7i76e.0.stepgen.00.dirhold         5000
setp hm2_7i76e.0.stepgen.00.steplen         5000
setp hm2_7i76e.0.stepgen.00.stepspace       5000
setp hm2_7i76e.0.stepgen.00.position-scale  [JOINT_0]SCALE
setp hm2_7i76e.0.stepgen.00.maxaccel        [JOINT_0]STEPGEN_MAXACCEL
setp hm2_7i76e.0.stepgen.00.maxvel          [JOINT_0]STEPGEN_MAXVEL
setp hm2_7i76e.0.stepgen.00.step_type       0

net x-pos-cmd  joint.0.motor-pos-cmd  => hm2_7i76e.0.stepgen.00.position-cmd
net x-pos-fb   hm2_7i76e.0.stepgen.00.position-fb => joint.0.motor-pos-fb
net x-enable   joint.0.amp-enable-out => hm2_7i76e.0.stepgen.00.enable

# ─── Y AXIS (Joint 1) ────────────────────────────────
setp hm2_7i76e.0.stepgen.01.dirsetup        5000
setp hm2_7i76e.0.stepgen.01.dirhold         5000
setp hm2_7i76e.0.stepgen.01.steplen         5000
setp hm2_7i76e.0.stepgen.01.stepspace       5000
setp hm2_7i76e.0.stepgen.01.position-scale  [JOINT_1]SCALE
setp hm2_7i76e.0.stepgen.01.maxaccel        [JOINT_1]STEPGEN_MAXACCEL
setp hm2_7i76e.0.stepgen.01.maxvel          [JOINT_1]STEPGEN_MAXVEL
setp hm2_7i76e.0.stepgen.01.step_type       0

net y-pos-cmd  joint.1.motor-pos-cmd  => hm2_7i76e.0.stepgen.01.position-cmd
net y-pos-fb   hm2_7i76e.0.stepgen.01.position-fb => joint.1.motor-pos-fb
net y-enable   joint.1.amp-enable-out => hm2_7i76e.0.stepgen.01.enable

# ─── Z AXIS (Joint 2) ────────────────────────────────
setp hm2_7i76e.0.stepgen.02.dirsetup        5000
setp hm2_7i76e.0.stepgen.02.dirhold         5000
setp hm2_7i76e.0.stepgen.02.steplen         5000
setp hm2_7i76e.0.stepgen.02.stepspace       5000
setp hm2_7i76e.0.stepgen.02.position-scale  [JOINT_2]SCALE
setp hm2_7i76e.0.stepgen.02.maxaccel        [JOINT_2]STEPGEN_MAXACCEL
setp hm2_7i76e.0.stepgen.02.maxvel          [JOINT_2]STEPGEN_MAXVEL
setp hm2_7i76e.0.stepgen.02.step_type       0

net z-pos-cmd  joint.2.motor-pos-cmd  => hm2_7i76e.0.stepgen.02.position-cmd
net z-pos-fb   hm2_7i76e.0.stepgen.02.position-fb => joint.2.motor-pos-fb
net z-enable   joint.2.amp-enable-out => hm2_7i76e.0.stepgen.02.enable

# ─── E-STOP ──────────────────────────────────────────
net estop-ext  => iocontrol.0.emc-enable-in
{f'net estop-ext  <= hm2_7i76e.0.7i76.0.0.input-00' if config["has_estop"] else 'sets estop-ext true'}

# ─── HOME / LIMIT SWITCHES ───────────────────────────
# Adjust pin numbers to match your wiring!
"""
        if config["has_home_switches"]:
            hal += """\
net x-home  joint.0.home-sw-in  <= hm2_7i76e.0.7i76.0.0.input-01
net y-home  joint.1.home-sw-in  <= hm2_7i76e.0.7i76.0.0.input-02
net z-home  joint.2.home-sw-in  <= hm2_7i76e.0.7i76.0.0.input-03
"""

        if config["has_limit_switches"]:
            hal += """\
net x-limit  joint.0.neg-lim-sw-in joint.0.pos-lim-sw-in  <= hm2_7i76e.0.7i76.0.0.input-04
net y-limit  joint.1.neg-lim-sw-in joint.1.pos-lim-sw-in  <= hm2_7i76e.0.7i76.0.0.input-05
net z-limit  joint.2.neg-lim-sw-in joint.2.pos-lim-sw-in  <= hm2_7i76e.0.7i76.0.0.input-06
"""

        hal += f"""
# ─── SPINDLE ──────────────────────────────────────────
# Router control via relay (on/off)
net spindle-on  spindle.0.on  => hm2_7i76e.0.7i76.0.0.output-00

# ─── MACHINE ENABLE ──────────────────────────────────
net machine-is-on  halui.machine.is-on => hm2_7i76e.0.7i76.0.0.output-01
"""

    else:
        # Parallel port fallback (Option A / GRBL-like)
        hal = f"""\
# HAL Configuration — {name}
# Generated: {timestamp}
# Controller: Parallel Port (basic stepper setup)
#
# This is a basic parallel port configuration.
# For the Mesa 7i76e, regenerate with --controller mesa_7i76e.

loadrt trivkins
loadrt [EMCMOT]EMCMOT base_period_nsec=[EMCMOT]BASE_PERIOD servo_period_nsec=[EMCMOT]SERVO_PERIOD num_joints=3
loadrt stepgen step_type=0,0,0

addf stepgen.capture-position servo-thread
addf motion-command-handler servo-thread
addf motion-controller servo-thread
addf stepgen.update-freq servo-thread

# X Axis
setp stepgen.0.position-scale [JOINT_0]SCALE
setp stepgen.0.maxaccel [JOINT_0]STEPGEN_MAXACCEL
net x-pos-cmd joint.0.motor-pos-cmd => stepgen.0.position-cmd
net x-pos-fb stepgen.0.position-fb => joint.0.motor-pos-fb
net x-enable joint.0.amp-enable-out => stepgen.0.enable

# Y Axis
setp stepgen.1.position-scale [JOINT_1]SCALE
setp stepgen.1.maxaccel [JOINT_1]STEPGEN_MAXACCEL
net y-pos-cmd joint.1.motor-pos-cmd => stepgen.1.position-cmd
net y-pos-fb stepgen.1.position-fb => joint.1.motor-pos-fb
net y-enable joint.1.amp-enable-out => stepgen.1.enable

# Z Axis
setp stepgen.2.position-scale [JOINT_2]SCALE
setp stepgen.2.maxaccel [JOINT_2]STEPGEN_MAXACCEL
net z-pos-cmd joint.2.motor-pos-cmd => stepgen.2.position-cmd
net z-pos-fb stepgen.2.position-fb => joint.2.motor-pos-fb
net z-enable joint.2.amp-enable-out => stepgen.2.enable

# Spindle on/off relay
net spindle-on spindle.0.on
"""

    filepath = Path(output_dir) / f"{name}.hal"
    with open(filepath, "w") as f:
        f.write(hal)
    return filepath


def generate_tool_table(config, output_dir):
    """Generate a starter tool table."""
    name = config["machine_name"]
    tools = """\
; Tool Table — DIY CNC
; Format: T<number> P<pocket> D<diameter_mm> Z<offset_mm> ;comment
;
; Edit this file to match your actual tools.
; Measure tool lengths with a tool length sensor or manually.
;
T1  P1 D6.35  Z0.000  ;1/4" endmill
T2  P2 D3.175 Z0.000  ;1/8" endmill
T3  P3 D1.0   Z0.000  ;1mm engraving bit
T4  P4 D6.35  Z0.000  ;1/4" ball nose
T5  P5 D12.7  Z0.000  ;1/2" surfacing
T99 P0 D0.0   Z0.000  ;empty / no tool
"""
    filepath = Path(output_dir) / "tool.tbl"
    with open(filepath, "w") as f:
        f.write(tools)
    return filepath


def generate_postgui_hal(config, output_dir):
    """Generate postgui HAL (placeholder for UI connections)."""
    name = config["machine_name"]
    content = f"""\
# Post-GUI HAL — {name}
# Add any AXIS GUI panel connections here.
# This file is loaded after the GUI starts.
"""
    filepath = Path(output_dir) / "postgui.hal"
    with open(filepath, "w") as f:
        f.write(content)
    return filepath


def generate_all(config, output_dir):
    """Generate all config files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = []
    files.append(generate_ini(config, output_dir))
    files.append(generate_hal(config, output_dir))
    files.append(generate_tool_table(config, output_dir))
    files.append(generate_postgui_hal(config, output_dir))

    # Also save the config as JSON for reproducibility
    config_path = output_dir / f"{config['machine_name']}_config.json"
    import json
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    files.append(config_path)

    return files


# --- Interactive Configuration ---

def configure_interactive():
    """Walk through machine configuration interactively."""
    config = dict(DEFAULT_CONFIG)

    print("\n  --- LinuxCNC Configuration Generator ---")
    print("  Press Enter to accept defaults shown in [brackets].\n")

    config["machine_name"] = (
        input(f"  Machine name [{config['machine_name']}]: ").strip()
        or config["machine_name"]
    )

    # Controller
    print(f"\n  Controller board:")
    print(f"    [1] Mesa 7i76e (recommended for precision build)")
    print(f"    [2] Parallel port (basic/prototype)")
    ctrl = input(f"  Choice [1]: ").strip()
    if ctrl == "2":
        config["controller"] = "parallel_port"

    # Travel
    print(f"\n  Axis travel (mm):")
    for axis in ("x", "y", "z"):
        key = f"{axis}_travel_mm"
        try:
            val = input(f"    {axis.upper()}-axis [{config[key]:.0f}mm]: ").strip()
            if val:
                config[key] = float(val)
        except ValueError:
            pass

    # Screws
    print(f"\n  Ball screw pitch (mm per revolution):")
    for axis in ("x", "y", "z"):
        key = f"{axis}_screw_pitch_mm"
        try:
            val = input(f"    {axis.upper()}-axis [{config[key]:.0f}mm]: ").strip()
            if val:
                config[key] = float(val)
        except ValueError:
            pass

    # Steppers
    print(f"\n  Stepper motor configuration:")
    try:
        val = input(f"    Steps/rev [{config['steps_per_rev']}]: ").strip()
        if val:
            config["steps_per_rev"] = int(val)
        val = input(f"    Microstepping [{config['microstepping']}]: ").strip()
        if val:
            config["microstepping"] = int(val)
    except ValueError:
        pass

    # Speeds
    print(f"\n  Maximum velocities (mm/s):")
    for axis in ("x", "y", "z"):
        key = f"{axis}_max_vel_mm_s"
        try:
            val = input(f"    {axis.upper()}-axis [{config[key]:.0f}]: ").strip()
            if val:
                config[key] = float(val)
        except ValueError:
            pass

    # Switches
    print(f"\n  Switches and sensors:")
    for label, key in [("Home switches", "has_home_switches"),
                       ("Limit switches", "has_limit_switches"),
                       ("E-stop button", "has_estop"),
                       ("Touch probe", "has_probe")]:
        default = "y" if config[key] else "n"
        val = input(f"    {label}? (y/n) [{default}]: ").strip().lower()
        if val:
            config[key] = val == "y"

    return config


def interactive():
    print("\n" + "=" * 55)
    print("  LINUXCNC CONFIG GENERATOR")
    print("=" * 55)

    config = dict(DEFAULT_CONFIG)

    while True:
        print(f"\n  [1] Generate with defaults (Option B build)")
        print(f"  [2] Configure interactively, then generate")
        print(f"  [3] Show current config values")
        print(f"  [q] Quit")

        choice = input("\n  > ").strip().lower()

        if choice == "1":
            out_dir = Path(__file__).parent / "linuxcnc_output"
            files = generate_all(config, out_dir)
            print(f"\n  Generated {len(files)} files in {out_dir}/:")
            for f in files:
                print(f"    {f.name}")
            print(f"\n  Copy these to your LinuxCNC configs directory.")
            print(f"  REVIEW ALL VALUES before running on real hardware!")

        elif choice == "2":
            config = configure_interactive()
            out_dir = input(f"\n  Output directory [./linuxcnc_output]: ").strip()
            if not out_dir:
                out_dir = Path(__file__).parent / "linuxcnc_output"
            files = generate_all(config, out_dir)
            print(f"\n  Generated {len(files)} files in {out_dir}/:")
            for f in files:
                print(f"    {f.name}")

        elif choice == "3":
            print(f"\n  Current Configuration:")
            print(f"  {'─' * 45}")
            for k, v in config.items():
                print(f"    {k:<30s} = {v}")

        elif choice in ("q", "quit", "exit"):
            print("  Done.")
            break


def main():
    parser = argparse.ArgumentParser(description="LinuxCNC Config Generator for DIY CNC")
    sub = parser.add_subparsers(dest="command")

    p_gen = sub.add_parser("generate", help="Generate config files with defaults")
    p_gen.add_argument("--dir", default=None, help="Output directory")
    p_gen.add_argument("--controller", choices=["mesa_7i76e", "parallel_port"],
                       default="mesa_7i76e", help="Controller board type")

    args = parser.parse_args()

    if args.command == "generate":
        config = dict(DEFAULT_CONFIG)
        config["controller"] = args.controller
        out_dir = args.dir or str(Path(__file__).parent / "linuxcnc_output")
        files = generate_all(config, out_dir)
        print(f"\n  Generated {len(files)} files in {out_dir}/:")
        for f in files:
            print(f"    {f.name}")
        print(f"\n  Review all values before use!")
    else:
        interactive()


if __name__ == "__main__":
    main()
