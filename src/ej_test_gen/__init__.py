"""
# ejudge test generator

# Example1:
from ej_test_gen import TestRunner, random
runner = TestRunner(solution="sol.py", tests_dir="tests")
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
        tests_dir='tests',

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

        # 'default': raise RuntimeError when solution fails
        # 'ignore': skip failed tests
        # 'output': save stderr/traceback as the answer
        on_error='default',
)

# By default, relative solution and tests_dir paths are resolved from the
# directory of the script creating TestRunner. Pass working_dir explicitly
# when you want another base directory; working_dir='.' resolves paths from
# the process current working directory.
#
# Old on_error aliases are still accepted:
# 'raise' -> 'default', 'skip' -> 'ignore'.
"""

from .__about__ import *
from .ej_test_gen import *
