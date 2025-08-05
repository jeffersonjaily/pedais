#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

py::array_t<float> apply_delay(py::array_t<float> input,
                              float time_ms = 300.0f,
                              float feedback = 0.4f,
                              float mix = 0.3f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    // Delay buffer simples - tamanho fixo em amostras
    size_t delay_samples = static_cast<size_t>((time_ms / 1000.0f) * 44100.0f);

    std::vector<float> delay_buffer(delay_samples, 0.0f);
    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    for (size_t i = 0; i < size; i++) {
        float delayed = i < delay_samples ? 0.0f : delay_buffer[i % delay_samples];
        float wet = ptr[i] * (1.0f - mix) + delayed * mix;
        res_ptr[i] = wet;

        delay_buffer[i % delay_samples] = ptr[i] + delayed * feedback;
    }

    return result;
}
