// derived from https://github.com/mrjohnk/PMW3360DM-T2QU

#include <pico/stdlib.h>
#include <hardware/gpio.h>

#include "pmw3360.h"

#include "registers.h"
#include "srom.h"

extern "C" {
#include <stdio.h>
#include "pio_spi.h"
}

void PMW3360_pair::init() {

	for (uint8_t i = 0; i < 2; ++i)
	{
		gpio_init(sensors[i].ncs_pin);
		gpio_set_dir(sensors[i].ncs_pin, GPIO_OUT);
		gpio_put(sensors[i].ncs_pin, 1);

		uint offset = pio_add_program(sensors[i].spi.pio, &spi_cpha1_program);

		float clkdiv = 62.5f/2; /* 500KHz @ 125 clk_sys */
		bool cpha = 1;
		bool cpol = 1;
		pio_spi_init(sensors[i].spi.pio, sensors[i].spi.sm,
					 offset, 8, clkdiv, cpha, cpol,
					 sensors[i].sck_pin,
					 sensors[i].mosi_pin,
					 sensors[i].miso_pin);
	}

	perform_startup();
}

void PMW3360_pair::set_cpi(unsigned int cpi) {
	int cpival = (cpi / 100) - 1;
	write_register(Config1, cpival);
}

void PMW3360_pair::update() {
	// write 0x01 to Motion register and read from it to freeze the motion values and make them available
	write_register(Motion, 0x01);

	uint8_t m[2];

	uint8_t v[2];
	read_registers(Motion, v);
	is_on_surface = !((v[0] | v[1]) & (1 << 3));

	m[0] |= v[0];
	m[1] |= v[1];

	read_registers(Delta_X_L, v);
	movement[0][0] = v[0];
	movement[1][0] = v[1];

	m[0] |= v[0];
	m[1] |= v[1];

	read_registers(Delta_X_H, v);
	movement[0][0] |= ((int16_t) v[0]) << 8;
	movement[1][0] |= ((int16_t) v[1]) << 8;

	m[0] |= v[0];
	m[1] |= v[1];

	read_registers(Delta_Y_L, v);
	movement[0][1] = v[0];
	movement[1][1] = v[1];

	m[0] |= v[0];
	m[1] |= v[1];

	read_registers(Delta_Y_H, v);
	movement[0][1] |= ((int16_t) v[0]) << 8;
	movement[1][1] |= ((int16_t) v[1]) << 8;

	m[0] |= v[0];
	m[1] |= v[1];

	if ((m[0] == 0 && m[1] != 0) || (m[0] != 0 && m[1] == 0))
	{
		dead_sensor_frames++;

		if (dead_sensor_frames > 100)
		{
			printf("Restarting sensors\n");
			perform_startup();
			dead_sensor_frames == 0;
		}
	}
}

void PMW3360_pair::cs_select(uint8_t sensor) {
	asm volatile("nop \n nop \n nop");
	gpio_put(sensors[sensor].ncs_pin, 0);  // Active low
	asm volatile("nop \n nop \n nop");
}

void PMW3360_pair::cs_deselect(uint8_t sensor) {
	asm volatile("nop \n nop \n nop");
	gpio_put(sensors[sensor].ncs_pin, 1);
	asm volatile("nop \n nop \n nop");
}

void PMW3360_pair::read_registers(uint8_t reg_addr, uint8_t (&v)[2]) {
	cs_select(0);
	cs_select(1);

	// send adress of the register, with MSBit = 0 to indicate it's a read
	uint8_t x = reg_addr & 0x7f;
	pio_spi_write8_blocking(&sensors[0].spi, &x, 1);
	pio_spi_write8_blocking(&sensors[1].spi, &x, 1);
	sleep_us(100);	// tSRAD
	// read data
	pio_spi_read8_blocking(&sensors[0].spi, &v[0], 1);
	pio_spi_read8_blocking(&sensors[1].spi, &v[1], 1);

	sleep_us(1);  // tSCLK-NCS for read operation is 120ns
	cs_deselect(0);
	cs_deselect(1);
	sleep_us(19);  // tSRW/tSRR (=20us) minus tSCLK-NCS
}

void PMW3360_pair::write_register(uint8_t reg_addr, uint8_t data) {
	cs_select(0);
	cs_select(1);

	// send adress of the register, with MSBit = 1 to indicate it's a write
	uint8_t x = reg_addr | 0x80;
	pio_spi_write8_blocking(&sensors[0].spi, &x, 1);
	pio_spi_write8_blocking(&sensors[1].spi, &x, 1);

	// send data
	pio_spi_write8_blocking(&sensors[0].spi, &data, 1);
	pio_spi_write8_blocking(&sensors[1].spi, &data, 1);

	sleep_us(20);  // tSCLK-NCS for write operation
	cs_deselect(0);
	cs_deselect(1);
	sleep_us(100);	// tSWW/tSWR (=120us) minus tSCLK-NCS. Could be shortened, but is looks like a safe lower bound
}


void PMW3360_pair::perform_startup() {
	for (uint8_t i=0; i < 2; ++i)
	{
		cs_deselect(i);						   // ensure that the serial port is reset
		cs_select(i);						   // ensure that the serial port is reset
		cs_deselect(i);						   // ensure that the serial port is reset
	}

	write_register(Power_Up_Reset, 0x5a);  // force reset
	sleep_ms(50);						   // wait for it to reboot

	// read registers 0x02 to 0x06 (and discard the data)
	uint8_t v[2];
	read_registers(Motion, v);
	read_registers(Delta_X_L, v);
	read_registers(Delta_X_H, v);
	read_registers(Delta_Y_L, v);
	read_registers(Delta_Y_H, v);

	// upload the firmware
	upload_firmware();
	sleep_ms(10);
}

void PMW3360_pair::upload_firmware() {
	// send the firmware to the chip, cf p.18 of the datasheet

	// Write 0 to Rest_En bit of Config2 register to disable Rest mode.
	write_register(Config2, 0x20);

	// write 0x1d in SROM_enable reg for initializing
	write_register(SROM_Enable, 0x1d);

	// wait for more than one frame period
	sleep_ms(10);  // assume that the frame rate is as low as 100fps... even if it should never be that low

	// write 0x18 to SROM_enable to start SROM download
	write_register(SROM_Enable, 0x18);

	for (uint8_t i=0; i<2; ++i)
	{
		// write the SROM file (=firmware data)
		cs_select(i);
		uint8_t data = SROM_Load_Burst | 0x80;	// write burst destination adress
		pio_spi_write8_blocking(&sensors[i].spi, &data, 1);
		sleep_us(15);

		// send all bytes of the firmware
		for (int j = 0; j < firmware_length; j++) {
			pio_spi_write8_blocking(&sensors[i].spi, &(firmware_data[j]), 1);
			sleep_us(15);
		}

		cs_deselect(i);
	}

	// Read the SROM_ID register to verify the ID before any other register reads or writes.
	// (and discard data)
	uint8_t v[2];
	read_registers(SROM_ID, v);

	// Write 0x00 to Config2 register for wired mouse or 0x20 for wireless mouse design.
	write_register(Config2, 0x00);

	// set initial CPI resolution
	write_register(Config1, 0x15);
}
