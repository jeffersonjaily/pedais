from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'effects_cpp',
        sources=[
            'Afinador.cpp',
            'BOSS_BF_2_Flanger.cpp',
            'CarmillaDistortion.cpp',
            'chorus.cpp',
            'chorusCE2.cpp',
            'compressor_guitarra.cpp',
            'delay.cpp',
            'distortion.cpp',
            'equalizer.cpp',
            'fuzz.cpp',
            'overdrive.cpp',
            'reverb.cpp',
            'tremolo.cpp',
            'tuner.cpp',
            'Ultra_Flanger_UF100.cpp',
            'VintageOverdrive.cpp',
            'wahwah.cpp',
            'bindings.cpp',
        ],
        include_dirs=[pybind11.get_include()],
        language='c++',
        extra_compile_args=['-std=c++11'],
    )
]

setup(
    name='effects_cpp',
    ext_modules=ext_modules,
)
