#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// Afinador geralmente só analisa, aqui só retorna buffer zerado como exemplo
py::array_t<float> apply_afinador(py::array_t<float> input) {
    auto buf = input.request();
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Exemplo: zerar o buffer para "silenciar" durante afinador
    for (size_t i = 0; i < size; i++) {
        res_ptr[i] = 0.0f;
    }

    return result;
}
