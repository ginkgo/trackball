from build123d import *
from enum import Enum
import argparse
import os

### Configuration enum types

# Type of ball suspension used
class SuspensionType(Enum):
    BEARING_BALL = 1
    BALL_TRANSFER_UNIT = 2

class CableMountType(Enum):
    # Simple hole in the back to lead cable connected to RaspPi Pico to
    HOLE = 1

    # USB-C plug in back
    USBC_PLUG = 2

    # Use a RP2040 Super-Mini board instead of pi pico and place it in back so
    # the USB-C plug can be used directly
    RP2040_SUPERMINI = 3

class SwitchPCBType(Enum):
    # Jacek Fedoryński's key switch PCB
    JFEDOR2 = 1

    # G304/G305 replacement key switch PCB
    G304 = 2

### Config type and parser

class TrackballConfig():
    def __init__(self, ball, switch_pcb_type, suspension_type, cable_mount_type, bearing):
        self.ball = ball
        self.switch_pcb_type = switch_pcb_type
        self.suspension_type = suspension_type
        self.cable_mount_type = cable_mount_type
        self.bearing = bearing

        self.outdir = "output"
        self.gen_stl = False
        self.gen_step = False
        self.split_buttons = False

    def parse_cmdline_args(self):
        parser = argparse.ArgumentParser(description="Generates trackball parts")
        parser.add_argument('-o', '--outdir', type=str, default=self.outdir, help='Output directory')
        parser.add_argument('--stl', action='store_true', default=self.gen_stl, help='Generate STL files')
        parser.add_argument('--step', action='store_true', default=self.gen_step, help='Generate STEP files')
        parser.add_argument('--ballsize', type=float, default=self.ball, help='Size of trackball in mm')
        parser.add_argument('--suspension_type', type=str, default=self.suspension_type.name,
                            choices=[e.name for e in SuspensionType], help='Suspension type')
        parser.add_argument('--cable_mount_type', type=str, default=self.cable_mount_type.name,
                            choices=[e.name for e in CableMountType], help='Cable mount type')
        parser.add_argument('--switch_pcb_type', type=str, default=self.switch_pcb_type.name,
                            choices=[e.name for e in SwitchPCBType], help='Keyswitch PCB type')
        parser.add_argument('--bearing', type=float, default=self.bearing,
                            help='Bearing ball size (only used for static BEARING_BALL suspension)')
        parser.add_argument('--split-buttons', action='store_true', default=self.split_buttons, help='Split out front of buttons so they can be colored differently (Mk.II only)')

        args = parser.parse_args()

        self.ball = args.ballsize
        self.switch_pcb_type = SwitchPCBType[args.switch_pcb_type]
        self.suspension_type = SuspensionType[args.suspension_type]
        self.cable_mount_type = CableMountType[args.cable_mount_type]
        self.bearing = args.bearing
        self.outdir = args.outdir
        self.gen_stl = args.stl
        self.gen_step = args.step
        self.split_buttons = args.split_buttons

        if not args.stl and not args.step:
            print("Skipping generation (use --stl or --step)")
            exit(0)

def write_files(config, result):
    if config.gen_stl or config.gen_step:
        os.makedirs(config.outdir, exist_ok=True)

    if config.gen_stl:
        for k,v in result.items():
            print(k)
            exporter = Mesher()
            exporter.add_shape(v)
            exporter.write(f'{config.outdir}/{k}.stl')
    if config.gen_step:
        for k,v in result.items():
            print(k)
            export_step(v, f'{config.outdir}/{k}.step')

### Utility functions, constants, and parts

print_resolution = 0.1

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

def prusa_trick_borehole(radius, depth, counter_bore_radius, counter_bore_depth):
    loc = Pos(0,0,1)

    part = Cylinder(radius, counter_bore_depth + depth, align=align('cc+'))
    part += Cylinder(counter_bore_radius, counter_bore_depth + 1, align=align('cc+'))
    part += (Box(2*radius, 2*counter_bore_radius, counter_bore_depth + 1 + print_resolution, align=align('cc+')) &
             Cylinder(counter_bore_radius, counter_bore_depth + 1 + print_resolution, align=align('cc+')))
    part += Box(2*radius, 2*radius, counter_bore_depth + 1 + 2*print_resolution, align=align('cc+'))

    return loc * part

# Measurements for 7.5mm YK310 ball transfer unit (from datasheet)
btu_D  = 9
btu_D1 = 7.5
btu_L  = 4
btu_L1 = 1.1
btu_H  = 1

# Bore holes for screws
M3x4 = prusa_trick_borehole(radius=1.45, depth=5, counter_bore_radius=3.1, counter_bore_depth=1.2)
M2x3 = CounterBoreHole(radius=0.95, depth=4, counter_bore_radius=2.1, counter_bore_depth=0.7)
M2x4 = CounterBoreHole(radius=0.95, depth=5, counter_bore_radius=2.1, counter_bore_depth=0.7)
M2x6 = CounterBoreHole(radius=0.95, depth=7, counter_bore_radius=2.1, counter_bore_depth=0.7)

eta = 0.1 # General tolerance
