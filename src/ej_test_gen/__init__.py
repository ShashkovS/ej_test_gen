"""
# ejudge test generator

# Example1:
from ej_test_gen import TestRunner, random
runner = TestRunner(solution="sol.py")
runner.test("3")

# sol.py
n = int(input())
fct = 1
for i in range(2, n + 1):
    fct *= i
print(fct)

# Example2:
runner2 = TestRunner(
        solution='sol.py',
        tests_path='.',

        test_name_template='{:02}',
        test_is_binary=False,
        test_encoding="utf-8",

        ans_name_template='{:02}.a',
        ans_encoding="utf-8",
        ans_is_binary=False,

        py_executable=sys.executable,
        cpp_compiler="g++",
        timeout=5,
        use_WSL=False,
        compilation_timeout=30,
)
"""

from .__about__ import *
from .ej_test_gen import *
