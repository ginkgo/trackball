from build123d import *
import sys

def align(xyz):
    d = {'c': Align.CENTER,
         '-': Align.MIN,
         '+': Align.MAX}
    return [d[c] for c in xyz]

# Measurements for 7.5mm YK310 ball transfer unit (from datasheet)
btu_D  = 9
btu_D1 = 7.5
btu_L  = 4
btu_L1 = 1.1
btu_H  = 1

pullout_size = 2
pullout_depth = 1

tool = Box(btu_D + pullout_size, 50, pullout_size, align=align('c-c'))
tool -= Box(btu_D, 15, pullout_size+2, align=align('c-c'))
tool -= Pos(0,pullout_depth/2,0) * Box(btu_D+pullout_size/2, 2, pullout_size+2, align=align('c-c'))

result = {
    'tool': tool,
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
