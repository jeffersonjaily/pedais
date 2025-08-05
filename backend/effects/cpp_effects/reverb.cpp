#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

py::array_t<float> apply_reverb(py::array_t<float> input,
                               float mix = 0.3f,
                               float size = 0.7f,
                               float decay = 0.5f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size_audio = buf.size;

    py::array_t<float> result(size_audio);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Simples reverb placeholder (delay + decay)
    size_t delay_samples = static_cast<size_t>(size * 44100);

    std::vector<float> delay_buffer(delay_samples, 0.0f);

    for (size_t i = 0; i < size_audio; i++) {
        float delayed = i < delay_samples ? 0.0f : delay_buffer[i % delay_samples];
        res_ptr[i] = ptr[i] * (1.0f - mix) + delayed * mix;

        delay_buffer[i % delay_samples] = ptr[i] + delayed * decay;
    }

    return result;
}
