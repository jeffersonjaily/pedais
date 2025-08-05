#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <vector>

namespace py = pybind11;

// Recebe o array de bandas (float[]) para ganho em cada banda
py::array_t<float> apply_equalizer(py::array_t<float> input,
                                  std::vector<float> bands) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    size_t size = buf.size;

    py::array_t<float> result(size);
    auto res_buf = result.request();
    float* res_ptr = static_cast<float*>(res_buf.ptr);

    // Simples aplicação multiplicativa banda a banda
    for (size_t i = 0; i < size; i++) {
        float gain = 1.0f;
        if (bands.size() > 0) gain += bands[0] / 15.0f;
        if (bands.size() > 1) gain += bands[1] / 15.0f;
        if (bands.size() > 2) gain += bands[2] / 15.0f;
        if (bands.size() > 3) gain += bands[3] / 15.0f;
        if (bands.size() > 4) gain += bands[4] / 15.0f;
        if (bands.size() > 5) gain += bands[5] / 15.0f;
        if (bands.size() > 6) gain += bands[6] / 15.0f;

        res_ptr[i] = ptr[i] * gain;
    }

    return result;
}
