from build123d import *
from enum import Enum

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
