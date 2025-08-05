#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif


namespace py = pybind11;

py::array_t<float> apply_boss_bf_2_flanger(py::array_t<float> input,
                                           float rate = 3.0f,
                                           float depth = 0.7f,
                                           float manual = 0.5f,
                                           float resonance = 0.4f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Exemplo de flanger muito simplificado: delay + modulação
    for (size_t i = 0; i < size; i++) {
        float mod = depth * std::sin(2 * M_PI * rate * i / 44100.0f);
        size_t delay_idx = i > static_cast<size_t>(manual * 441) ? i - static_cast<size_t>(manual * 441) : 0;
        res_ptr[i] = ptr[i] + resonance * ptr[delay_idx] * mod;
    }

    return result;
}
