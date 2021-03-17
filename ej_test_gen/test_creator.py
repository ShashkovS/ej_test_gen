from ej_test_gen import TestRunner, random
runner = TestRunner(solution="sol.py")
# runner = TestRunner(solution="sol.cpp", use_WSL=True)
# runner = TestRunner(solution="sol.py", use_WSL=True, py_executable='python3.8')

runner.test("""3""")
runner.test("""5""")

for tests_in_group, group_max in [(2, 10), (5, 50)]:
    for __ in range(tests_in_group):
        n = random.randint(0, group_max)
        test = f'{n}'
        runner.test(test)

#
#
# from ej_test_gen import TestRunner, random
# runner = TestRunner(solution="sol.py")
# runner = TestRunner(solution="sol.cpp")
# runner = TestRunner(solution="sol.cpp", use_WSL=True)
# # sudo apt install software-properties-common
# # sudo add-apt-repository ppa:deadsnakes/ppa
# # sudo apt install python3.8
# runner = TestRunner(solution="sol.py", use_WSL=True, py_executable='python3.8')
#
# runner.test("""\
# 3""")
#
# runner.test("""\
# 15""")
#
# for tests_in_group, group_max in [(2, 10), (5, 50)]:
#     for __ in range(tests_in_group):
#         n = random.randint(0, group_max)
#         test = f'{n}'
#         runner.test(test)
