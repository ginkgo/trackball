# Experimental 3D Space Mouse Mode

I recently added support in firmware that allows using the trackball as a space mouse for full 3 axis rotations.

This requires building a separate firmware version for now. In principle it should be possible for one firmware build to support both trackball and space mouse mode and switching between them on the fly but that's not implemented yet.

I've only tested this on Linux with [spacenavd](http://github.com/FreeSpacenav/spacenavd) so far.

## Building the firmware

Follow the general firmware build instructions, but add the `-DDEVICETYPE=SPACEMOUSE` option when configuring.

```
cd firmware
mkdir build
cd build
cmake .. -DBOARD=<board_type> -DTRACKBALL=<trackball_version> -DDEVICETYPE=SPACEMOUSE
make -j8
```

This generates a `trackball.uf2` which you can upload to your board.

## Using the Device

Install `spacenavd` and add the following config option to `/etc/spnavrc`:

```
device-id = cafe:ba3d
```

This is the dummy USB device ID reported by the trackball in spacemouse mode.
Then start the `spacenavd` daemon.

With this any software that supports `libspnav` should now allow you to control rotations using the trackball. I've tested Blender and FreeCAD and they work.
You probably need to tune sensitivity and swap some axes depending on the used application. You can do that with the `spnavcfg` tool.

Blender by default locks the rotation of one axis. To fix this change the 'Orbit Method' from 'Turntable' to 'Trackball' under 'Navigation' in the Preferences.

FreeCAD needs "Swap Y-Z" enabled and RY inverted in spnavcfg. It also needs to have the sensitivity lowered significantly.
