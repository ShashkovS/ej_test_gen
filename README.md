# Create tests for ejudge using solution

## Install
```bash
pip install git+https://github.com/ShashkovS/ej_test_gen.git --user --upgrade
```

## Example:

```python
# sol.py
n = int(input())
fct = 1
for i in range(2, n + 1):
    fct *= i
print(fct)
```

```python
# test_creator.py
from ej_test_gen import TestRunner, random
runner = TestRunner(solution="sol.py", tests_dir="tests")
# runner = TestRunner(solution="sol.cpp", tests_dir="tests", use_WSL=True)

runner.test("""3""")
runner.test("""5""")

for tests_in_group, group_max in [(2, 10), (5, 50)]:
    for __ in range(tests_in_group):
        n = random.randint(0, group_max)
        test = f'{n}'
        runner.test(test)
```


```bash
> python test_creator.py
001: 3         -->    6¶                                           Done! 0.27c
002: 2         -->    2¶                                           Done! 0.25c
003: 3         -->    6¶                                           Done! 0.26c
004: 31        -->    8222838654177922817725562880000000¶          Done! 0.25c
005: 10        -->    3628800¶                                     Done! 0.26c
006: 15        -->    1307674368000¶                               Done! 0.26c
007: 41        -->    3345252661316380710817006205344075166515     Done! 0.27c
008: 15        -->    1307674368000¶                               Done! 0.27c
```

`TestRunner` resolves relative `solution` and `tests_dir` paths from the
directory of the script where `TestRunner` is created. This means `sol.py` and
`test_creator.py` can live in the same directory, and generated tests will be
written to `tests/` next to them even if you run the script from another
directory:

```bash
python path/to/test_creator.py
```

Pass `working_dir` explicitly when you want a different base directory. For
example, `working_dir="."` keeps the old behavior where relative paths are
resolved from the process current working directory.

## Solution errors

Use `on_error` to choose what happens when the solution exits with a non-zero
return code or writes to stderr:

```python
# default: stop generation and raise RuntimeError
runner = TestRunner(solution="sol.py", tests_dir="tests")

# ignore: skip failed tests and keep generating the next ones
runner = TestRunner(solution="sol.py", tests_dir="tests", on_error="ignore")

# output: write stderr/traceback to the answer file
runner = TestRunner(solution="sol.py", tests_dir="tests", on_error="output")
```

Old names are still accepted for compatibility: `on_error="raise"` means
`on_error="default"`, and `on_error="skip"` means `on_error="ignore"`.


# License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.
