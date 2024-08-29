from ej_test_gen import TestRunner, random

runner = TestRunner(solution="sol.cpp", use_WSL=True)

runner.test("""3""")
runner.test("""5""")

for tests_in_group, group_max in [(2, 10), (5, 50)]:
    for __ in range(tests_in_group):
        n = random.randint(0, group_max)
        test = f'{n}'
        runner.test(test)
