# Trackball

This is a 3d-printable twist-to-scroll trackball using a Raspberry Pi Pico and two PMW3360 sensors designed using [build123d](https://github.com/gumyr/build123d).

![my trackball](img/img1.jpeg)

It's based on [jfedor2](https://github.com/jfedor2)'s excellent set of projects.
In particular it's using 2 [PMW3360 breakout PCBs](https://github.com/jfedor2/pmw3360-breakout) and 4 [mouse buttons switch mount PCBs](https://github.com/jfedor2/mouse-switch-mount-pcb). It's also using a firmware derived from his [twist-to-scroll trackball](https://github.com/jfedor2/twist-to-scroll-trackball) project.

However there's a number of pretty major changes:

Instead of a [RP2040+PMW3360](https://github.com/jfedor2/rp2040-pmw3360) board I'm using a regular Raspberry Pi Pico.

![opened trackball](img/img3.jpeg)

I redesigned the entire enclosure from the ground up in build123d. The nice thing about this is that it should be possible to parameterize the generated model (for instance to use a 55mm trackball instead of a 57.2mm billiards ball or to change the type of bearing used).

The button assembly is quite different and feels a lot better in my opinion.

The sensors are arranged at a 45-degree angle to move them as low as possible and keep them out of the way of the button assembly.
This means when reading from the sensors, some axis values (the X and Z axis) need to be reconstructed from a combination values from both sensors.

This is done in firmware. The basic math isn't too complicated, but it meant that the time delay between reading both sensors should be minimal or else the time lag might show up as unintended twists around the Z axis.
To improve this I interleaved the sensor access. I also switched from RP2040 HW SPI to PIO SPI which allowed for more flexible GPIO mapping.

## Configuring and generating the models

![the models](img/img2.png)

The enclosure parts are all defined in the `trackball.py` file.

You can generate the `STL` or `STEP` files by calling

```
$ python3 trackball.py STL
```
or
```
$ python3 trackball.py STEP
```
respectively from a python environment with `build123d` available.
(I personally use STEP since export is faster and my slicing tool takes it just fine)

All the major configuration options can be found in the beginning of the file. The most important ones are probably the trackball diameter and the type of suspension and cable mount to use.

By default we use a 57.2mm billiards size ball, a ball transfer unit suspension and set up an opening for a [USB-C plug](https://www.aliexpress.com/item/1005007593502706.html).
```
BALL = 57.2
suspension_type = SuspensionType.BALL_TRANSFER_UNIT
cable_mount_type = CableMountType.USBC_PLUG
switch_pcb_type = SwitchPCBType.G304
```

## Building the firmware

To build the firmware you need to have `pico-sdk` installed.
Then configure and build using CMake:

```
cd firmware
mkdir build
cd build
cmake .. -DBOARD=<board_type>
make -j8
```

This generates a `trackball.uf2` which you can upload to your board.

`<board_type>` is the type of microcontroller board you want to target. Possible options are `RPI_PICO` for a regular RaspberryPi Pico or `RP2040_SUPERMINI` for a RP2040 supermini board.

## 3D printing
These are the parts you need to print:

* `bottom`
  The base plate for the entire assembly. Doesn't need supports.
* `top`
  The top cover of the trackball. Needs supports.
* `button0`, `button1`, `button2`, `button3`
  The top buttons. Each one has a different curvature so they're not interchangeable. Need supports.
* `strip0`
  The flexible springs to hold the button in place. You need 4 of these but they're all identical. Doesn't need supports when printed on their side.

I printed everything with PLA and a layer size of 0.1mm.

The printed models shouldn't need too much cleanup apart from the contact surface between the buttons and the underside of the top cover.
Any residue supports must be removed. I found this area also needs a bit of manual filing and adjustment until the button clickiness feels right.
I used needle files for this.

## Parts

Apart from the 3d-printed parts you need the following:

* 1 microcontroller board. Either:
  * A RaspberryPi Pico
    This should be easy to find but you will need to do some extra soldering for the USB cable.
  * A [RP2040 Supermini](https://www.eelectronicparts.com/products/rp2040-super-mini-pico-compatible-with-raspberry-pi-micro-python-2mb-flash)
    This plugs directly into the USB socket in the back of the trackball so less soldering necessary.
	`cable_mount_type = CableMountType.RP2040_SUPERMINI`
* 2 [PMW3360 breakout PCBs](https://github.com/jfedor2/pmw3360-breakout) with a PMW3360 sensor soldered in.
  These will need to be ordered from a service like JLCPCB or PCBWay. You will find the Gerber files and BOM on jfedor's github.
* 4 keyswitch mount PCBs with a D2F type switch. You have two options here:
  * Custom order jfedor's [mouse switch mount PCB](https://github.com/jfedor2/mouse-switch-mount-pcb)
    `switch_pcb_type = SwitchPCBType.JFEDOR2`
  * Buy 2 pairs of [G304/G305 button replacement PCBs](https://vi.aliexpress.com/item/1005004663221786.html).
    `switch_pcb_type = SwitchPCBType.G304`
* 3 YK310 type BTUs (or steel/ruby/ceramic bearings with an adapter)
* Machine screws
  * M3x4 (For bottom screws)
  * M2x3 (For almost everything else)
  * M1.6x3 (In case you use G304/G305 button PCBs)
* A [USB-C socket](https://vi.aliexpress.com/item/1005007593502706.html)
  * in case you use a RaspberryPi Pico board.
* Various cabling and solder supplies
  * I recommend getting pairs of JST male/female cables so breakout boards can be attached after soldering.

## Wiring

Here's some rough wiring diagrams for both board configurations.
You can change the GPIO pins used in `firmware/src/trackball.cc` if you want to move things around.

I recommend using JST cables to connect the microcontroller and the breakout boards.

### Wiring (RaspberryPi Pico)
![RaspberryPi Pico wiring diagram](img/rpi_pico_wiring.png)

### Wiring (RP2040 Supermini)
![RP2040 Supermini wiring diagram](img/rp2040_supermini_wiring.png)

## Assembly

Once you printed out your parts and wired everything up you should be ready to assemble your trackball.
This should hopefully be relatively straightforward.

* Screw the various boards to the bottom plate.
* Screw flexible strips to the button parts and place the assembled buttons over the switches.
* Place the top part over everything and secure it with the screws on the bottom (and back).
* Push in your bearing of choice.

The bit that's probably easiest to mix up is which button goes where. The best way to tell which is which is to look at their curvature. Front buttons have a much steeper angle and the lowest part protudes below the attachment point for the flexible strip.
You should also be able to tell by the layer lines from the 3d print.

![front vs back buttons](img/front_vs_back_button_curvature.png)

## Minor tips and tricks

The trackball can be configured to either use ball transfer units (7.5mm [YK310 or YK311](https://www.aliexpress.com/item/1005005528750648.html) type from aliexpress) or have small indentations to press in small steel or zirconium bearing balls.

However I found it's most flexible to just adapt an enclosure for ball transfer units to bearing balls using a small 3d-printed adapter.

![different ball transfer units and bearing ball adapters](img/img5.jpeg)

You can find the pregenerated models for the adapter in the `stl` and `step` folders and the script to generate it in `adapter.py`.

## Experience

I've been using this trackball for a couple months now. Initially I was kind of struggling finding a type of bearing I like.
At least the cheap BTUs didn't quite feel right. I ended up with using static ruby bearings for my current setup which I tend to like best.
The pool balls I'm using aren't the highest quality and noticeable uneven in places. I should eventually try to get something better. (I ordered a set of Kandy Pearlized balls that got recommended, but these didn't seem to work with my PMW3360 sensors)

![my home setup](img/img4.jpeg)
![my work setup](img/img6.jpeg)

## Future Work

The front buttons tend to be stiff when printed out of the box. While this can be fixed with a bit of filing I think the underlying problem is that the angle of contact between the button and top part is too steep. This should probably be redesigned.

I'm planning to make a wrist-rest that attaches using neodymium magnets in the enclosure. I'd probably try printing it in TPU.

Similarly I'd like to make a magnetically attached top cover for easy transport.

The firmware could need quite a bit of cleanup.
Alternatively adding support for this trackball in QMK might also be an option.
I've looked a bit into this and I would likely have to change how things are wired up for QMK to work.

I don't yet know how durable the 3d-printed PLA springs holding the buttons in place will be (I guess it's easy to just reprint them if they break) but if this turns out to be a common point of failure it might be possible to replace them with a strip of steel.

Using PIO it should be possible to access both sensors in perfect lock-step by having them share a single SCLK, NCS, and MOSI pin and having two separate MISO pins that are read at once.

In principle it should be possible to CNC machine all parts in metal. This would likely need a bit of cleanup to some parts but nothing major.

## License

The 3d-printable parts as well as the python code to generate thes is copyright 2024 Thomas Weber and licensed under terms the MIT license.

The firmware is copyright 2024 Thomas Weber, copyright 2021 Jacek Fedoryński (jfedor2), and copyright 2019 Ha Thach (tinyusb.org) and licensed under the terms of the MIT license.
There is also a piece of code for the SPI PIO copyright 2020 of the Raspberry Pi that's licensed under the terms of the BSD-3-Clause license.
