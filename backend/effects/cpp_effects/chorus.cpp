#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

py::array_t<float> apply_chorus(py::array_t<float> input,
                                std::string mode = "chorus",
                                float rate = 2.0f,
                                float width = 0.003f,
                                float intensity = 0.7f,
                                float tone = 5.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Exemplo simples de chorus (modulação)
    for (size_t i = 0; i < size; i++) {
        float mod = intensity * std::sin(2 * M_PI * rate * i / 44100.0f);
        res_ptr[i] = ptr[i] + width * mod * ptr[i];
    }

    return result;
}
