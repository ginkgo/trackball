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

void PMW3360::init() {

	gpio_init(ncs_pin);
	gpio_set_dir(ncs_pin, GPIO_OUT);
	gpio_put(ncs_pin, 1);

	uint offset = pio_add_program(spi.pio, &spi_cpha1_program);
	
	float clkdiv = 62.5f/2; /* 500KHz @ 125 clk_sys */
	bool cpha = 1;
	bool cpol = 1;
	pio_spi_init(spi.pio, spi.sm, offset, 8, clkdiv, cpha, cpol, sck_pin, mosi_pin, miso_pin);

	perform_startup();
}

void PMW3360::set_cpi(unsigned int cpi) {
	int cpival = (cpi / 100) - 1;
	cs_select();
	write_register(Config1, cpival);
	cs_deselect();
}

void PMW3360::update() {
	// write 0x01 to Motion register and read from it to freeze the motion values and make them available
	write_register(Motion, 0x01);
	uint8_t motion = read_register(Motion);

	is_on_surface = !(motion & (1 << 3));

	movement[0] = read_register(Delta_X_L);
	movement[0] |= ((int16_t) read_register(Delta_X_H)) << 8;
	movement[1] = read_register(Delta_Y_L);
	movement[1] |= ((int16_t) read_register(Delta_Y_H)) << 8;
}

void PMW3360::cs_select() {
	asm volatile("nop \n nop \n nop");
	gpio_put(ncs_pin, 0);  // Active low
	asm volatile("nop \n nop \n nop");
}

void PMW3360::cs_deselect() {
	asm volatile("nop \n nop \n nop");
	gpio_put(ncs_pin, 1);
	asm volatile("nop \n nop \n nop");
}

uint8_t PMW3360::read_register(uint8_t reg_addr) {
	cs_select();

	// send adress of the register, with MSBit = 0 to indicate it's a read
	uint8_t x = reg_addr & 0x7f;
	pio_spi_write8_blocking(&spi, &x, 1);
	sleep_us(100);	// tSRAD
	// read data
	uint8_t data;
	pio_spi_read8_blocking(&spi, &data, 1);

	sleep_us(1);  // tSCLK-NCS for read operation is 120ns
	cs_deselect();
	sleep_us(19);  // tSRW/tSRR (=20us) minus tSCLK-NCS

	return data;
}

void PMW3360::write_register(uint8_t reg_addr, uint8_t data) {
	cs_select();

	// send adress of the register, with MSBit = 1 to indicate it's a write
	uint8_t x = reg_addr | 0x80;
	pio_spi_write8_blocking(&spi, &x, 1);
	
	// send data
	pio_spi_write8_blocking(&spi, &data, 1);

	sleep_us(20);  // tSCLK-NCS for write operation
	cs_deselect();
	sleep_us(100);	// tSWW/tSWR (=120us) minus tSCLK-NCS. Could be shortened, but is looks like a safe lower bound
}


void PMW3360::perform_startup() {
	cs_deselect();						   // ensure that the serial port is reset
	cs_select();						   // ensure that the serial port is reset
	cs_deselect();						   // ensure that the serial port is reset
	write_register(Power_Up_Reset, 0x5a);  // force reset
	sleep_ms(50);						   // wait for it to reboot
	// read registers 0x02 to 0x06 (and discard the data)
	read_register(Motion);
	read_register(Delta_X_L);
	read_register(Delta_X_H);
	read_register(Delta_Y_L);
	read_register(Delta_Y_H);
	// upload the firmware
	upload_firmware();
	sleep_ms(10);
}

void PMW3360::upload_firmware() {
	// send the firmware to the chip, cf p.18 of the datasheet

	// Write 0 to Rest_En bit of Config2 register to disable Rest mode.
	write_register(Config2, 0x20);

	// write 0x1d in SROM_enable reg for initializing
	write_register(SROM_Enable, 0x1d);

	// wait for more than one frame period
	sleep_ms(10);  // assume that the frame rate is as low as 100fps... even if it should never be that low

	// write 0x18 to SROM_enable to start SROM download
	write_register(SROM_Enable, 0x18);

	// write the SROM file (=firmware data)
	cs_select();
	uint8_t data = SROM_Load_Burst | 0x80;	// write burst destination adress
	pio_spi_write8_blocking(&spi, &data, 1);
	sleep_us(15);

	// send all bytes of the firmware
	for (int i = 0; i < firmware_length; i++) {
		pio_spi_write8_blocking(&spi, &(firmware_data[i]), 1);
		sleep_us(15);
	}

	// Read the SROM_ID register to verify the ID before any other register reads or writes.
	read_register(SROM_ID);

	// Write 0x00 to Config2 register for wired mouse or 0x20 for wireless mouse design.
	write_register(Config2, 0x00);

	// set initial CPI resolution
	write_register(Config1, 0x15);

	cs_deselect();
}
