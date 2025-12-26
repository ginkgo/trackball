from build123d import *
import sys
from trackball_common import *

# This generates an adapter from an enclosure designed for YK310 ball transfer units
# to a regular bearing ball suspensions. This is useful for evaluating the different bearing options.

# All measurements in millimeters

## Default configuration:
config = TrackballConfig(57.2, # pool billiards ball
                         SwitchPCBType.G304,
                         SuspensionType.BALL_TRANSFER_UNIT,
                         CableMountType.RP2040_SUPERMINI,
                         2.5)

if __name__ == '__main__':
    config.parse_cmdline_args()

# Bearing diameter
bearing = config.bearing

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

adapter  = Pos(0,0,btu_L1) * Cylinder(radius=btu_D1/2, height=btu_H + btu_L, align=align('cc-'))
adapter += Pos(0,0,btu_L1) * Cylinder(radius=btu_D/2, height=btu_H, align=align('cc-'))

adapter -= Cylinder(bearing/2, bearing, align=align('cc-'))
# adapter += Sphere(bearing/2, align=align('cc-'))

top_edge = adapter.edges().sort_by(Axis.Z)[-1]

adapter = chamfer([top_edge], 1)

result = {
    f'adapter_{bearing}mm': adapter,
}

write_files(config, result)
