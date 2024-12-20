# Distributed under the OSI-approved BSD 3-Clause License.  See accompanying
# file Copyright.txt or https://cmake.org/licensing for details.

cmake_minimum_required(VERSION 3.5)

file(MAKE_DIRECTORY
  "C:/Users/scrap/esp/esp-idf/components/bootloader/subproject"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/tmp"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/src/bootloader-stamp"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/src"
  "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/src/bootloader-stamp"
)

set(configSubDirs )
foreach(subDir IN LISTS configSubDirs)
    file(MAKE_DIRECTORY "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/src/bootloader-stamp/${subDir}")
endforeach()
if(cfgdir)
  file(MAKE_DIRECTORY "E:/Tech/Projects/LOTP-3DOF_Cable_Driven_Parallel_Robot/res/ESP-IDF/espcam_module/build/bootloader-prefix/src/bootloader-stamp${cfgdir}") # cfgdir has leading slash
endif()
