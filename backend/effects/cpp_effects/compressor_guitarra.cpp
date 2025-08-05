#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>

namespace py = pybind11;

py::array_t<float> apply_compressor_guitarra(py::array_t<float> input,
                                             float threshold_db = -20.0f,
                                             float ratio = 4.0f,
                                             float attack_ms = 10.0f,
                                             float release_ms = 200.0f,
                                             float level = 5.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    float threshold = std::pow(10.0f, threshold_db / 20.0f);

    for (size_t i = 0; i < size; i++) {
        float input_sample = ptr[i];
        float abs_sample = std::fabs(input_sample);

        if (abs_sample > threshold) {
            float compressed = threshold + (abs_sample - threshold) / ratio;
            res_ptr[i] = (input_sample < 0 ? -compressed : compressed) * (level / 10.0f);
        } else {
            res_ptr[i] = input_sample * (level / 10.0f);
        }
    }

    return result;
}
