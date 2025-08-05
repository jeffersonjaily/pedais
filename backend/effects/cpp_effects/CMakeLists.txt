cmake_minimum_required(VERSION 3.15)
project(audio_effects LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)

# Adiciona pybind11 (assume que está instalado no sistema)
find_package(pybind11 REQUIRED)

# Lista de arquivos .cpp
set(SOURCES
    Afinador.cpp
    BOSS_BF_2_Flanger.cpp
    CarmillaDistortion.cpp
    chorus.cpp
    chorusCE2.cpp
    compressor_guitarra.cpp
    delay.cpp
    distortion.cpp
    equalizer.cpp
    fuzz.cpp
    overdrive.cpp
    pedal_control.cpp
    PureSky.cpp
    reverb.cpp
    tremolo.cpp
    tuner.cpp
    Ultra_Flanger_UF100.cpp
    VintageOverdrive.cpp
    wahwah.cpp
    bindings.cpp  # Deve conter os bindings do pybind11
)

# Cria módulo Python
pybind11_add_module(audio_effects MODULE ${SOURCES})
