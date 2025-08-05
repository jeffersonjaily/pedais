#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>

namespace py = pybind11;

py::array_t<float> apply_overdrive(py::array_t<float> input,
                                  float gain = 5.0f,
                                  float tone = 5.0f,
                                  float level = 7.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    for (size_t i = 0; i < size; i++) {
        float val = ptr[i] * gain / 10.0f;
        // Clip
        if (val > 1.0f) val = 1.0f;
        else if (val < -1.0f) val = -1.0f;

        // Placeholder para tone (não implementado real)
        float toned = val * (tone / 10.0f);

        res_ptr[i] = toned * (level / 10.0f);
    }

    return result;
}
