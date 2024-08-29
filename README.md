# Create tests for ejudge using solution

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
runner = TestRunner(solution="sol.py")
# runner = TestRunner(solution="sol.cpp", use_WSL=True)

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


# License

This is free and unencumbered software released into the public domain.

Anyone is free to copy, modify, publish, use, compile, sell, or distribute this software, either in source code form or as a compiled binary, for any purpose, commercial or non-commercial, and by any means.
