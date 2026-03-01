# Trackball Mk.I

This is the first version of my DIY trackball. 

![Trackball Mk.I](img/img1.jpeg)

It's significantly different from the second version ([Mk.II](trackball_mkii.md)) which completely redesigned the outer housing.
Personally I think the new version is just overall easier to build and nicer to use but I'm keeping this for posterity.

The old design requires a lot more individual parts that need to be printed and screwed together. On the plus side it's possible to use a regular RaspberryPi Pico board:

![opened trackball](img/img3.jpeg)

## Getting started

You can download tarballs with pregenerated parts and firmware under "Releases". 
If you want to do this yourself you can find details further below.

The Mk.I model allows a bunch of possible configurations regarding what size ball to use and what kind of switch and MCU PCBs to use.

## 3D printing
These are the parts you need to print:

* `bottom`
  * The base plate for the entire assembly. Doesn't need supports.
* `top`
  * The top cover of the trackball. Needs supports.
* `button0`, `button1`, `button2`, `button3`
  * The top buttons. Each one has a different curvature so they're not interchangeable. Need supports.
* `strip0`, `strip1`, `strip2`, `strip3`
  * The flexible springs to hold the button in place. You need 4 of these but they come in identical pairs (two shorter ones for the front and two longer ones for the back). Doesn't need supports when printed on the side.
* `adapter_X.Ymm` (optional)
  * Adapter if you want to use a static bearing to hold the trackball (instead of a BTU)
  * The `X.Ymm` number is the diameter of the bearing. So for instance `adapter_2.5mm` is for 2.5mm bearing balls.

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
	`--cable-mount-type RP2040_SUPERMINI`
* 2 [PMW3360 breakout PCBs](https://github.com/jfedor2/pmw3360-breakout) with a PMW3360 sensor soldered in.
  These will need to be ordered from a service like JLCPCB or PCBWay. You will find the Gerber files and BOM on jfedor's github.
* 4 keyswitch mount PCBs with a D2F type switch. You have two options here:
  * Custom order jfedor's [mouse switch mount PCB](https://github.com/jfedor2/mouse-switch-mount-pcb)
    `--switch_pcb_type JFEDOR2`
  * Buy 2 pairs of [G304/G305 button replacement PCBs](https://vi.aliexpress.com/item/1005004663221786.html).
    `--switch_pcb_type G304`
* 1 57.2mm billiards ball
  * Or a 55mm trackball if you adjust the ball size in the script
* 3 YK310 type BTUs (or steel/ruby/ceramic bearings with an adapter)
* 4 10x2mm cylindric neodymium magnets (for attaching wrist-rest in Mk.II)
  * The magnets in the main unit can also be thicker
* Machine screws
  * M3x4 (For bottom screws)
  * M2x3 (For almost everything else)
  * M1.6x3 (In case you use G304/G305 button PCBs)
* A [USB-C socket](https://vi.aliexpress.com/item/1005007593502706.html)
  * in case you use a RaspberryPi Pico board.
* Various cabling and solder supplies
  * I recommend getting pairs of JST male/female cables so breakout boards can be attached after soldering.
* Some adhesive rubber feet or strips so the trackball doesn't slip.

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

You can open all the model files in a 3d editor like blender to see where everything goes.

The bit that's probably easiest to mix up is which button goes where. The best way to tell which is which is to look at their curvature. Front buttons have a much steeper angle and the lowest part protudes below the attachment point for the flexible strip.
You should also be able to tell by the layer lines from the 3d print.

![front vs back buttons](img/front_vs_back_button_curvature.png)

## Minor tips and tricks

The trackball can be configured to either use ball transfer units (7.5mm [YK310 or YK311](https://www.aliexpress.com/item/1005005528750648.html) type from aliexpress) or have small indentations to press in small steel or zirconium bearing balls.

However I found it's most flexible to just adapt an enclosure for ball transfer units to bearing balls using a small 3d-printed adapter.

![different ball transfer units and bearing ball adapters](img/img5.jpeg)

You can find the pregenerated models for the adapter in the `stl` and `step` folders and the script to generate it in `adapter.py`.

## Experience

I've been using the Mk.I trackball for about a year now. Initially I was kind of struggling finding a type of bearing I like.
At least the cheap BTUs didn't quite feel right. I ended up with using static ruby bearings for my current setup which I tend to like best.
The pool balls I'm using aren't the highest quality and noticeable uneven in places. I should eventually try to get something better. (I ordered a set of Kandy Pearlized balls that got recommended, but these didn't seem to work with my PMW3360 sensors)

![my home setup](img/img4.jpeg)
![my work setup](img/img6.jpeg)

In principle it should be possible to CNC machine all parts for the Mk.I trackball in metal. (Mk.II is trickier) This would likely need a bit of cleanup to some parts but nothing major.

One persistent problem the Mk.I has is that the front buttons tend to get stuck when you click them. This can be "improved" by filing down the underside of the enclosure, but that leads to loose buttons. Theoretically the proper fix would be to change the angle in which the buttons protrude, but I ended up going for a complete revamp with the Mk.II instead.

## Configuring and generating the models

![Trackball Mk.II blueprint](img/mkii_blueprint.png)

The enclosure parts are generated by the `trackball.py` script.
They use `build123d` and I generally recommend using `uv` to run them like this:
You can generate the `STL` or `STEP` files by calling

```
$ uv run --with build123d trackball.py --step --outdir mk1
```

This generates `.step` model files in the `mk1` subdir.
You can also use PyPI or Conda to install `build123d` instead.

There's more configuration options. Call the scripts with `--help` for details.

## Building the firmware

To build the firmware you need to have `pico-sdk` installed.
Then configure and build using CMake:

```
cd firmware
mkdir build
cd build
cmake .. -DBOARD=<board_type> -DTRACKBALL=<trackball_version>
make -j8
```

This generates a `trackball.uf2` which you can upload to your board.

`<board_type>` is the type of microcontroller board you want to target. Possible options are `RPI_PICO` for a regular RaspberryPi Pico or `RP2040_SUPERMINI` for a RP2040 supermini board.
`<trackball_version>` is the version of the trackball to generate. This is either `MK_I` for the Mk.I version or `MK_II` for the Mk.II version.
