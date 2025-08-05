// Esse arquivo pode conter funções auxiliares para controle geral dos pedais,
// ou manipulação de parâmetros, etc. Dependendo do seu projeto, pode ser deixado vazio
// ou conter funções para ligar/desligar efeito, bypass, etc.

#include <pybind11/pybind11.h>

namespace py = pybind11;

void bypass(bool on) {
    // Implementa bypass (exemplo placeholder)
}

PYBIND11_MODULE(pedal_control, m) {
    m.def("bypass", &bypass, "Ativa ou desativa bypass");
}
