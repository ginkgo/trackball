#!/usr/bin/env bash

declare -A config0=(
	[version]='MK_I'
	[ballsize]='57.2'
	[cable_mount]='USBC_PLUG'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config1=(
	[version]='MK_I'
	[ballsize]='57.2'
	[cable_mount]='HOLE'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config2=(
	[version]='MK_I'
	[ballsize]='57.2'
	[cable_mount]='RP2040_SUPERMINI'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config3=(
	[version]='MK_I'
	[ballsize]='55'
	[cable_mount]='USBC_PLUG'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config4=(
	[version]='MK_I'
	[ballsize]='55'
	[cable_mount]='HOLE'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config5=(
	[version]='MK_I'
	[ballsize]='55'
	[cable_mount]='RP2040_SUPERMINI'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config6=(
	[version]='MK_I'
	[ballsize]='52'
	[cable_mount]='USBC_PLUG'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config7=(
	[version]='MK_I'
	[ballsize]='52'
	[cable_mount]='HOLE'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config8=(
	[version]='MK_I'
	[ballsize]='52'
	[cable_mount]='RP2040_SUPERMINI'
	[suspension]='BALL_TRANSFER_UNIT'
)

declare -A config9=(
	[version]='MK_II'
	[ballsize]='57.2'
	[cable_mount]='RP2040_SUPERMINI'
	[suspension]='BALL_TRANSFER_UNIT'
)

mkdir -p release
rm -rf release/*

declare -n config
for config in ${!config@}; do
	name="ginkgo_trackball_${config[version]}_${config[ballsize]}mm_${config[cable_mount]}"
	echo Generating $name

	mkdir -p output
	rm -rf output/*

	if [ "${config[version]}" = MK_I ]; then
		generator_name=trackball.py
	else
		generator_name=trackball2.py
	fi

	if [ "${config[cable_mount]}" = RP2040_SUPERMINI ]; then
		board_type=RP2040_SUPERMINI
	else
		board_type=RPI_PICO
	fi

	uv run --with build123d $generator_name \
	   --step --stl --outdir output \
	   --ball ${config[ballsize]} \
	   --switch_pcb_type G304 \
	   --cable_mount_type ${config[cable_mount]} \
	   --suspension_type ${config[suspension]}

	f3d --line-width 3.0 -j -p --anti-aliasing --anti-aliasing-mode=ssaa \
		--multi-file-mode all \
		--camera-direction -1,-1,-0.5 \
		--filename=false \
		--axis=false \
		--input output/*.step \
		--output output/preview_front.png
	
	f3d --line-width 3.0 -j -p --anti-aliasing --anti-aliasing-mode=ssaa \
		--multi-file-mode all \
		--camera-direction 1,1,-0.5 \
		--filename=false \
		--axis=false \
		--input output/*.step \
		--output output/preview_back.png
	
	if [ "${config[suspension]}" = BALL_TRANSFER_UNIT ]; then
		uv run --with build123d ./adapter.py --step --stl --outdir output --bearing 2.0
		uv run --with build123d ./adapter.py --step --stl --outdir output --bearing 2.5
		uv run --with build123d ./adapter.py --step --stl --outdir output --bearing 3.0
		uv run --with build123d ./adapter.py --step --stl --outdir output --bearing 3.5
	fi

	# Delete unnecessary models
	rm output/ball*
	rm output/*pcb*
	rm output/pipico*

	mkdir -p firmware/build
	rm -rf firmware/build/*
	cd firmware/build
	cmake .. -DBOARD=$board_type -DTRACKBALL="${config[version]}"
	make -j8
	cd -

	pkgdir=release/$name
	mkdir -p $pkgdir

	echo "Trackball version: ${config[version]}" >> $pkgdir/configuration
	echo "Ball size: ${config[ballsize]}" >> $pkgdir/configuration
	echo "Cable mount type: ${config[cable_mount]}" >> $pkgdir/configuration
	echo "Suspension type: ${config[suspension]}" >> $pkgdir/configuration

	mkdir $pkgdir/step
	mv output/*.step $pkgdir/step
	mkdir $pkgdir/stl
	mv output/*.stl $pkgdir/stl
	convert output/preview_front.png $pkgdir/preview_front.jpeg
	convert output/preview_back.png $pkgdir/preview_back.jpeg

	cp firmware/build/*.uf2 $pkgdir/

	if [ "${config[cable_mount]}" = RP2040_SUPERMINI ]; then
		cp img/rp2040_supermini_wiring.png $pkgdir/wiring.png
	else
		cp img/rpi_pico_wiring.png $pkgdir/wiring.png
	fi

	tar -czvf release/$name.tar.gz -C release $name

done
