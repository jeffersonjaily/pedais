#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>

namespace py = pybind11;

// Declarações (prototipos) das funções para cada efeito
py::array_t<float> apply_afinador(py::array_t<float> input);

py::array_t<float> apply_boss_bf_2_flanger(py::array_t<float> input,
                                           float rate,
                                           float depth,
                                           float manual,
                                           float resonance);

py::array_t<float> apply_carmilladistortion(py::array_t<float> input,
                                            float gain,
                                            float tone,
                                            float level);

py::array_t<float> apply_chorus(py::array_t<float> input,
                                std::string mode,
                                float rate,
                                float width,
                                float intensity,
                                float tone);

py::array_t<float> apply_chorusce2(py::array_t<float> input,
                                   float rate,
                                   float depth);

py::array_t<float> apply_compressor_guitarra(py::array_t<float> input,
                                             float threshold_db,
                                             float ratio,
                                             float attack_ms,
                                             float release_ms,
                                             float level);

py::array_t<float> apply_delay(py::array_t<float> input,
                               float time_ms,
                               float feedback,
                               float mix);

py::array_t<float> apply_distortion(py::array_t<float> input,
                                    float drive,
                                    float level);

py::array_t<float> apply_equalizer(py::array_t<float> input,
                                   std::vector<float> bands);

py::array_t<float> apply_fuzz(py::array_t<float> input,
                              float gain,
                              float mix);

py::array_t<float> apply_overdrive(py::array_t<float> input,
                                   float gain,
                                   float tone,
                                   float level);

py::array_t<float> apply_reverb(py::array_t<float> input,
                                float mix,
                                float size,
                                float decay);

py::array_t<float> apply_tremolo(py::array_t<float> input,
                                 float rate,
                                 float depth);

py::array_t<float> apply_tuner(py::array_t<float> input);

py::array_t<float> apply_ultra_flanger_uf100(py::array_t<float> input,
                                             float rate,
                                             float depth,
                                             float resonance,
                                             float manual);

py::array_t<float> apply_vintageoverdrive(py::array_t<float> input,
                                          float drive,
                                          float tone,
                                          float level);

py::array_t<float> apply_wahwah(py::array_t<float> input,
                                float rate,
                                float min_freq,
                                float max_freq,
                                float q);

// PYBIND11_MODULE: nome do módulo para import no Python
PYBIND11_MODULE(effects_cpp, m) {
    m.doc() = "Efeitos de áudio em C++ para Python";

    m.def("apply_afinador", &apply_afinador, "Aplicar Afinador Cromático");

    m.def("apply_boss_bf_2_flanger", &apply_boss_bf_2_flanger,
          py::arg("input"),
          py::arg("rate") = 3.0f,
          py::arg("depth") = 0.7f,
          py::arg("manual") = 0.5f,
          py::arg("resonance") = 0.4f,
          "Aplicar BOSS BF-2 Flanger");

    m.def("apply_carmilladistortion", &apply_carmilladistortion,
          py::arg("input"),
          py::arg("gain") = 12.0f,
          py::arg("tone") = 6.0f,
          py::arg("level") = 7.0f,
          "Aplicar Carmilla Distortion");

    m.def("apply_chorus", &apply_chorus,
          py::arg("input"),
          py::arg("mode") = "chorus",
          py::arg("rate") = 2.0f,
          py::arg("width") = 0.003f,
          py::arg("intensity") = 0.7f,
          py::arg("tone") = 5.0f,
          "Aplicar Chorus");

    m.def("apply_chorusce2", &apply_chorusce2,
          py::arg("input"),
          py::arg("rate") = 4.0f,
          py::arg("depth") = 0.75f,
          "Aplicar Chorus CE-2");

    m.def("apply_compressor_guitarra", &apply_compressor_guitarra,
          py::arg("input"),
          py::arg("threshold_db") = -20.0f,
          py::arg("ratio") = 4.0f,
          py::arg("attack_ms") = 10.0f,
          py::arg("release_ms") = 200.0f,
          py::arg("level") = 5.0f,
          "Aplicar Compressor para Guitarra");

    m.def("apply_delay", &apply_delay,
          py::arg("input"),
          py::arg("time_ms") = 300.0f,
          py::arg("feedback") = 0.4f,
          py::arg("mix") = 0.3f,
          "Aplicar Delay");

    m.def("apply_distortion", &apply_distortion,
          py::arg("input"),
          py::arg("drive") = 10.0f,
          py::arg("level") = 5.0f,
          "Aplicar Distortion");

    m.def("apply_equalizer", &apply_equalizer,
          py::arg("input"),
          py::arg("bands"),
          "Aplicar Equalizador Gráfico");

    m.def("apply_fuzz", &apply_fuzz,
          py::arg("input"),
          py::arg("gain") = 15.0f,
          py::arg("mix") = 1.0f,
          "Aplicar Fuzz");

    m.def("apply_overdrive", &apply_overdrive,
          py::arg("input"),
          py::arg("gain") = 5.0f,
          py::arg("tone") = 5.0f,
          py::arg("level") = 7.0f,
          "Aplicar Overdrive");

    m.def("apply_reverb", &apply_reverb,
          py::arg("input"),
          py::arg("mix") = 0.3f,
          py::arg("size") = 0.7f,
          py::arg("decay") = 0.5f,
          "Aplicar Reverb");

    m.def("apply_tremolo", &apply_tremolo,
          py::arg("input"),
          py::arg("rate") = 5.0f,
          py::arg("depth") = 0.8f,
          "Aplicar Tremolo");

    m.def("apply_tuner", &apply_tuner,
          py::arg("input"),
          "Aplicar Afinador");

    m.def("apply_ultra_flanger_uf100", &apply_ultra_flanger_uf100,
          py::arg("input"),
          py::arg("rate") = 2.0f,
          py::arg("depth") = 0.8f,
          py::arg("resonance") = 0.5f,
          py::arg("manual") = 0.6f,
          "Aplicar Ultra Flanger UF-100");

    m.def("apply_vintageoverdrive", &apply_vintageoverdrive,
          py::arg("input"),
          py::arg("drive") = 6.0f,
          py::arg("tone") = 4.0f,
          py::arg("level") = 8.0f,
          "Aplicar Vintage Overdrive");

    m.def("apply_wahwah", &apply_wahwah,
          py::arg("input"),
          py::arg("rate") = 1.5f,
          py::arg("min_freq") = 400.0f,
          py::arg("max_freq") = 2000.0f,
          py::arg("q") = 5.0f,
          "Aplicar Wah Wah");
}
