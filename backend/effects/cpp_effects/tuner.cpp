#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

py::array_t<float> apply_tuner(py::array_t<float> input) {
    auto buf = input.request();
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Tuner não altera o áudio
    for (size_t i = 0; i < size; i++) {
        res_ptr[i] = 0.0f; // pode deixar zerado ou copiar input se quiser
    }

    return result;
}
