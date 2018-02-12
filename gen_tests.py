# -*- coding: utf-8 -*-.

import subprocess
import os
import time
import sys
from random import *

_current_path = os.path.dirname(os.path.abspath(__file__))

# Удаляем старые тесты
for filename in os.listdir(_current_path):
    testname = filename
    if testname.endswith('.a'):
        testname = testname[:-2]
    if testname.isdigit() and int(testname) > 100:
        os.remove(os.path.join(_current_path, filename))


def _run(to_stdin='', module_name='dummy_sol.py'):
    """Запускач тестов"""
    module_full_path = os.path.join(_current_path, module_name) # Считаем, что модуль лежит в текущей директории
    st = time.time()
    with open('input.txt', 'w', encoding='utf-8') as f:
        f.write(to_stdin)
    pr = subprocess.Popen([sys.executable, module_full_path], stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE) # Запускаем процесс
    stdout_data = pr.communicate(input=bytes(to_stdin, encoding='utf-8'), timeout=5) # Передаём данные в StdIN
    dur = time.time() - st # Засекаем время
    from_stdout = b''.join(stdout_data).rstrip().decode('utf-8') # Клеим ответ
    try:
        os.remove('input.txt')
    except OSError:
        pass
    return from_stdout, dur



_test_num = 100
_LEN = 40

def prc_test(test):
    global _test_num
    test = test.strip()
    _test_num += 1
    _test_num_str = '{:03}'.format(_test_num)
    print('{}: {}{}    -->    '.format(_test_num_str, test.replace('\n', '  ')[:_LEN].ljust(_LEN), '...' if test.replace('\n', '  ')[_LEN:] else '   '), end='')

    ans, dur = _run(test)

    if dur <= 5:
        print('{}{}  Done! {:.2}c'.format(ans.replace('\n', '  ')[:_LEN].ljust(_LEN), '...' if ans.replace('\n', '  ')[_LEN:] else '   ', dur))
        with open(_test_num_str, 'w') as f:
            f.write(str(test) + '\n')
        with open(_test_num_str + '.a', 'w') as f:
            f.write(str(ans) + '\n')
    else:
        print('timeout', '{:.2}c'.format(dur))


exec(open('test_creator.py').read())
