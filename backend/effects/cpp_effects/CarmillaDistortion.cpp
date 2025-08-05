#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <algorithm>

namespace py = pybind11;

py::array_t<float> apply_carmilladistortion(py::array_t<float> input,
                                            float gain = 12.0f,
                                            float tone = 6.0f,
                                            float level = 7.0f) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    for (size_t i = 0; i < size; i++) {
        // Simples distorção soft clipping
        float x = ptr[i] * gain / 20.0f;
        if (x > 1.0f) x = 1.0f;
        else if (x < -1.0f) x = -1.0f;

        // Ajusta tonalidade - só um placeholder (não é real)
        float toned = x * (tone / 10.0f);

        // Aplica nível final
        res_ptr[i] = toned * (level / 10.0f);
    }

    return result;
}
