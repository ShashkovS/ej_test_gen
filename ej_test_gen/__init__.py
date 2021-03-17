"""
ejudge test generator

Example:
from ej_test_gen import TestRunner, random
runner = TestRunner(solution="sol.py")
runner.test("3")

runner2 = TestRunner(
    solution='sol.py',
    test_path='.',
    test_encoding="utf-8",
    res_encoding="utf-8",
    test_is_binary=False,
    res_is_binary=False,
    res_suffix=".a",
    cpp_compiler="g++",
    py_executable=sys.executable,
    timeout=5,
    use_WSL=False,
    compilation_timeout=30,
)
"""

__version__ = '0.0.3'

from .ej_test_gen import *
