from build123d import *
import sys

# This generates an adapter from a top designed for YK310 ball transfer units
# to a regular bearing ball suspensions

# Bearing diameter
bearing = 2.5

original_ball = 57.2
target_ball = 55

assert(original_ball >= target_ball)

# Measurements for 7.5mm YK310 ball transfer unit (from datasheet)
btu_D  = 9
btu_D1 = 7.5
btu_L  = 4
btu_L1 = 1.1
btu_H  = 1

ball_diff = (original_ball - target_ball)/2

eta = 0.1 # General tolerance

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

adapter  = Pos(0,0,ball_diff + btu_L1) * Cylinder(radius=btu_D1/2, height=btu_H + btu_L, align=align('cc-'))
adapter += Pos(0,0,ball_diff + btu_L1) * Cylinder(radius=btu_D/2, height=btu_H, align=align('cc-'))
if ball_diff > 0:
    adapter += Pos(0,0,btu_L1) * Cone(bottom_radius=btu_D/3, top_radius=btu_D/2, height=ball_diff, align=align('cc-'))
adapter -= Cylinder(bearing/2, bearing, align=align('cc-'))
# adapter += Sphere(bearing/2, align=align('cc-'))

top_edge = adapter.edges().sort_by(Axis.Z)[-1]

adapter = chamfer([top_edge], 1)

result = {
    'adapter': adapter,
}


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} STL|STEP')
        exit(0)

    if sys.argv[1] == 'STL':
        for k,v in result.items():
            print(k)
            exporter = Mesher()
            exporter.add_shape(v)
            exporter.write(f'stl/{k}.stl')
    elif sys.argv[1] == 'STEP':

        for k,v in result.items():
            print(k)
            export_step(v, f'step/{k}.step')
    else:
        print(f'Usage: {sys.argv[0]} STL|STEP')
        exit(0)
