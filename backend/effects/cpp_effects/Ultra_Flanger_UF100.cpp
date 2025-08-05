#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>
#include <vector>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace py = pybind11;

py::array_t<float> apply_ultra_flanger_uf100(py::array_t<float> input,
                                             float rate = 2.0f,
                                             float depth = 0.8f,
                                             float resonance = 0.5f,
                                             float manual = 0.6f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    std::vector<float> delay_buffer(1000, 0.0f);  // buffer delay fixo (exemplo)

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    for (size_t i = 0; i < size; i++) {
        float mod = depth * std::sin(2 * M_PI * rate * i / 44100.0f);
        size_t delay_idx = i > 500 ? i - 500 : 0;

        float delayed = delay_buffer[delay_idx % delay_buffer.size()];
        res_ptr[i] = ptr[i] + resonance * delayed * mod;

        delay_buffer[i % delay_buffer.size()] = ptr[i] + delayed * manual;
    }

    return result;
}
