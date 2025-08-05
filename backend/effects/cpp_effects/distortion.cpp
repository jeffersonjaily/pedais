#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>

namespace py = pybind11;

py::array_t<float> apply_distortion(py::array_t<float> input,
                                   float drive = 10.0f,
                                   float level = 5.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    for (size_t i = 0; i < size; i++) {
        float val = ptr[i] * drive / 20.0f;
        // Soft clipping
        if (val > 1.0f) val = 1.0f;
        else if (val < -1.0f) val = -1.0f;

        res_ptr[i] = val * (level / 10.0f);
    }

    return result;
}
