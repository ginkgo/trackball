cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(trackball)

pico_sdk_init()

set(BOARD "RPI_PICO" CACHE STRING "Target board (RPI_PICO or RP2040_SUPERMINI)")
set(TRACKBALL "MK_I" CACHE STRING "Trackball version (MK_I or MK_II)")
set(DEVICETYPE "POINTING" CACHE STRING "USB device type (POINTING or SPACEMOUSE)")

set_property(CACHE BOARD PROPERTY STRINGS RPI_PICO RP2040_SUPERMINI)
set_property(CACHE TRACKBALL PROPERTY STRINGS MK_I MK_II)
set_property(CACHE DEVICETYPE PROPERTY STRINGS POINTING SPACEMOUSE)


if (TRACKBALL STREQUAL "MK_I")
  add_definitions(-DTRACKBALL_MK_I=1)
elseif(TRACKBALL STREQUAL "MK_II")
  add_definitions(-DTRACKBALL_MK_II=1)
else()
  message(FATAL_ERROR "Invalid option for TRACKBALL: ${TRACKBALL}")
endif()


if (BOARD STREQUAL "RPI_PICO")
  add_definitions(-DRPI_PICO=1)
elseif(BOARD STREQUAL "RP2040_SUPERMINI")
  add_definitions(-DRP2040_SUPERMINI=1)
else()
  message(FATAL_ERROR "Invalid option for BOARD: ${BOARD}")
endif()


if (DEVICETYPE STREQUAL "POINTING")
  add_definitions(-DPOINTING_DEVICE=1)
elseif(DEVICETYPE STREQUAL "SPACEMOUSE")
  add_definitions(-DSPACEMOUSE=1)
else()
  message(FATAL_ERROR "Invalid option for DEVICETYPE: ${DEVICETYPE}")
endif()

add_compile_options(-Wall)

add_executable(trackball src/trackball.cc src/pmw3360.cc src/srom.cc src/crc.cc src/pio_spi.c)

pico_generate_pio_header(trackball ${CMAKE_CURRENT_LIST_DIR}/src/spi.pio)

target_include_directories(trackball PRIVATE src)

target_link_libraries(trackball pico_stdlib hardware_flash hardware_pio tinyusb_device tinyusb_board)

pico_add_extra_outputs(trackball)
