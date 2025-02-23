cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(trackball)

pico_sdk_init()

option(BOARD "Select the type of board to target (RPI_PICO or RP2040_SUPERMINI)" "RPI_PICO")

if (BOARD STREQUAL "RPI_PICO")
  add_definitions(-DRPI_PICO=1)
elseif(BOARD STREQUAL "RP2040_SUPERMINI")
  add_definitions(-DRP2040_SUPERMINI=1)
else()
  message(FATAL_ERROR "Invalid option for BOARD: ${BOARD}")
endif()

add_compile_options(-Wall)

add_executable(trackball src/trackball.cc src/pmw3360.cc src/srom.cc src/crc.cc src/pio_spi.c)

pico_generate_pio_header(trackball ${CMAKE_CURRENT_LIST_DIR}/src/spi.pio)

target_include_directories(trackball PRIVATE src)

target_link_libraries(trackball pico_stdlib hardware_flash hardware_pio tinyusb_device tinyusb_board)

pico_add_extra_outputs(trackball)
