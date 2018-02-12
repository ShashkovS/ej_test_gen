# -*- coding: utf-8 -*-.

import subprocess
import os
import time
import sys
from random import *
from contest_tester import TestRunner

_current_path = os.path.dirname(os.path.abspath(__file__))

# Удаляем старые тесты
for filename in os.listdir(_current_path):
    testname = filename
    if testname.endswith('.a'):
        testname = testname[:-2]
    if testname.isdigit() and int(testname) > 100:
        os.remove(os.path.join(_current_path, filename))

_test_num = 100
_LEN = 40

runner = TestRunner(module_or_parm="dummy_sol.py")
def prc_test(test):
    global _test_num
    test = test.strip()
    _test_num += 1
    _test_num_str = '{:03}'.format(_test_num)
    print('{}: {}{}    -->    '.format(_test_num_str, test.replace('\n', '  ')[:_LEN].ljust(_LEN), '...' if test.replace('\n', '  ')[_LEN:] else '   '), end='')

    ans, dur = runner._run(test)
    if dur <= 5:
        print('{}{}  Done! {:.2}c'.format(ans.replace('\n', '  ')[:_LEN].ljust(_LEN), '...' if ans.replace('\n', '  ')[_LEN:] else '   ', dur))
        with open(_test_num_str, 'w') as f:
            f.write(test)
        with open(_test_num_str + '.a', 'w') as f:
            f.write(ans)
    else:
        print('timeout', '{:.2}c'.format(dur))


exec(open('test_creator.py').read())
