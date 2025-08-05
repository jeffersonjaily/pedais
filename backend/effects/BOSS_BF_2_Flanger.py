import numpy as np

class BossBf2Flanger:
    """
    Simula um pedal de efeito Flanger, inspirado no clássico BOSS BF-2.
    """

    def __init__(self, sample_rate: int):
        self.rate = sample_rate
        self.enabled = True

        self.manual = 0.5
        self.depth = 0.5
        self.lfo_rate = 1.0
        self.res = 0.5

        self.min_delay_ms = 0.5
        self.max_delay_ms = 5.0

        max_delay_samples = int(self.max_delay_ms / 1000 * self.rate)
        self.buffer_size = max_delay_samples + 2
        self.delay_buffer = np.zeros(self.buffer_size)
        self.write_pos = 0

        self.lfo_phase = 0.0
        self.last_delayed_sample = 0.0

    def _map_range(self, value, from_min, from_max, to_min, to_max):
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def apply(self, input_signal: np.ndarray, **params) -> np.ndarray:
        if not self.enabled:
            return input_signal

        self.manual = params.get("manual", self.manual)
        self.depth = params.get("depth", self.depth)
        self.lfo_rate = params.get("rate", self.lfo_rate)
        self.res = params.get("resonance", self.res)

        output_signal = np.zeros_like(input_signal)
        lfo_inc = 2 * np.pi * self.lfo_rate / self.rate

        for i, sample in enumerate(input_signal):
            lfo_value = np.sin(self.lfo_phase)
            self.lfo_phase = (self.lfo_phase + lfo_inc) % (2 * np.pi)

            center_delay = self._map_range(self.manual, 0.0, 1.0, self.min_delay_ms, self.max_delay_ms)
            sweep_depth_ms = self.depth * center_delay
            current_delay_ms = center_delay + lfo_value * sweep_depth_ms
            delay_samples = current_delay_ms / 1000.0 * self.rate

            read_pos_frac = self.write_pos - delay_samples
            read_pos_int = int(read_pos_frac)
            fraction = read_pos_frac - read_pos_int

            idx1 = read_pos_int % self.buffer_size
            idx2 = (read_pos_int + 1) % self.buffer_size

            val1 = self.delay_buffer[idx1]
            val2 = self.delay_buffer[idx2]
            delayed_sample = val1 + fraction * (val2 - val1)

            feedback_gain = self.res * 0.95
            input_with_feedback = sample + self.last_delayed_sample * feedback_gain

            self.delay_buffer[self.write_pos] = input_with_feedback
            self.write_pos = (self.write_pos + 1) % self.buffer_size

            output_signal[i] = 0.5 * sample + 0.5 * delayed_sample
            self.last_delayed_sample = delayed_sample

        return np.clip(output_signal, -1.0, 1.0)
