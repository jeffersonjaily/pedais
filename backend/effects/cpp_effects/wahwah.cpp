#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

py::array_t<float> apply_wahwah(py::array_t<float> input,
                                float rate = 1.5f,
                                float min_freq = 400.0f,
                                float max_freq = 2000.0f,
                                float q = 5.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Exemplo de filtro wah-wah simplificado
    for (size_t i = 0; i < size; i++) {
        float mod_freq = min_freq + (max_freq - min_freq) * (0.5f + 0.5f * std::sin(2 * M_PI * rate * i / 44100.0f));
        float mod = std::sin(mod_freq * i / 44100.0f);
        res_ptr[i] = ptr[i] * mod * q;
    }

    return result;
}
