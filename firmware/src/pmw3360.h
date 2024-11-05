#ifndef _PMW3360_H_
#define _PMW3360_H_

#include <hardware/spi.h>

extern "C" {
#include "pio_spi.h"
}

struct pmw3360_config {
	pio_spi_inst spi;
	uint miso_pin;
	uint mosi_pin;
	uint sck_pin;
	uint ncs_pin;
};

class PMW3360_pair {
public:
    PMW3360_pair(pmw3360_config config1, pmw3360_config config2) {
		sensors[0] = config1;
		sensors[1] = config2;
		dead_sensor_frames = 0;
	}
	
    void init();
    void set_cpi(unsigned int cpi);
    void update();

    int16_t movement[2][2];
    bool is_on_surface;
	int16_t dead_sensor_frames;

private:
	pmw3360_config sensors[2];

    void write_register(uint8_t reg_addr, uint8_t data);
    void read_registers(uint8_t reg_addr, uint8_t (&v)[2]);

	void cs_select(uint8_t sensor);
    void cs_deselect(uint8_t sensor);
    void perform_startup();
	void upload_firmware();
};

#endif
