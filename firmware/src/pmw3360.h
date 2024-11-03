#ifndef _PMW3360_H_
#define _PMW3360_H_

#include <hardware/spi.h>

extern "C" {
#include "pio_spi.h"
}

class PMW3360 {
public:
    PMW3360(PIO pio, uint sm, uint miso_pin, uint mosi_pin, uint sck_pin, uint ncs_pin)
        : spi({pio, sm}), miso_pin(miso_pin), mosi_pin(mosi_pin), sck_pin(sck_pin), ncs_pin(ncs_pin){};
    void init();
    void set_cpi(unsigned int cpi);
    void update();

    int16_t movement[2];
    bool is_on_surface;

private:
	pio_spi_inst spi;
    uint miso_pin;
    uint mosi_pin;
    uint sck_pin;
    uint ncs_pin;

    void cs_select();
    void cs_deselect();
    uint8_t read_register(uint8_t reg_addr);
    void write_register(uint8_t reg_addr, uint8_t data);
    void perform_startup();
    void upload_firmware();
};

#endif
