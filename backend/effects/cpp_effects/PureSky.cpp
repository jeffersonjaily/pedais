// Arquivo gerado automaticamente a partir de PureSky.py
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <cmath>

namespace py = pybind11;

py::array_t<float> apply_puresky(py::array_t<float> input, float gain, float volume) {
    auto buf = input.request();
    float* ptr = static_cast<float*>(buf.ptr);
    ssize_t n = buf.size;

    py::array_t<float> output(n);
    float* out = static_cast<float*>(output.request().ptr);

    for (ssize_t i = 0; i < n; i++) {
        float sample = ptr[i] * gain;
        // Clipping suave (soft clipping)
        sample = std::tanh(sample);  
        out[i] = sample * volume;
    }

    return output;
}

PYBIND11_MODULE(PureSky, m) {
    m.def("apply", &apply_puresky, "Aplica efeito PureSky",
          py::arg("input"), py::arg("gain") = 1.0f, py::arg("volume") = 1.0f);
}
