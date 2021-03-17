# -*- coding: utf-8 -*-.
import subprocess
import os
import time
import sys
import logging
import random

random.seed(2019)
logging.basicConfig(level=logging.INFO)
lg = logging.getLogger('Runner')

__all__ = ['TestRunner', 'random']

_current_path = os.getcwd()


class TestRunner:
    def __init__(self,
                 solution='sol.py',
                 *,
                 test_path=_current_path,
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
                 ):
        self.test_path = test_path
        self.py_executable = py_executable
        self.solution = solution
        self.test_encoding = test_encoding
        self.res_encoding = res_encoding
        self.test_is_binary = test_is_binary
        self.res_is_binary = res_is_binary
        self.res_suffix = res_suffix
        self.cpp_compiler = cpp_compiler
        self.timeout = timeout
        self.use_WSL = use_WSL
        self.compilation_timeout = compilation_timeout
        os.chdir(test_path)
        self.compile_sol()
        self._clean_up()


    def __repr__(self):
        return '{}(test_path = {!r}, py_executable = {!r}, solution = {!r}, test_encoding = {!r}, res_encoding = {!r}, ' \
               'test_is_binary = {!r}, res_is_binary = {!r}, res_suffix = {!r}, cpp_compiler = {!r}, timeout = {!r}, ' \
               'use_WSL = {!r}, compilation_timeout = {!r})'.format(
            self.__class__.__name__, self.test_path, self.py_executable, self.solution, self.test_encoding,
            self.res_encoding, self.test_is_binary, self.res_is_binary, self.res_suffix, self.cpp_compiler,
            self.timeout, self.use_WSL, self.compilation_timeout
        )

    def _run(self, to_stdin):
        if self.test_is_binary:
            input = to_stdin
        else:
            input = bytes(to_stdin, encoding=self.test_encoding)
        st = time.time()
        if self._compiled:
            to_run = ['./' + self._compiled]
        else:  # TODO Вообще-то, это если питон
            to_run = [self.py_executable, self.solution]
        to_run = ' '.join(to_run)
        if self.use_WSL:
            to_run = 'bash -c "{}"'.format(to_run)
        lg.debug(to_run)
        pr = subprocess.Popen(to_run,
                              stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                              cwd=self.test_path)
        stdout_data = pr.communicate(input=input, timeout=self.timeout)
        dur = time.time() - st
        stdout_data = b''.join(stdout_data)
        if self.res_is_binary:
            from_stdout = stdout_data
        else:
            from_stdout = stdout_data.decode(self.res_encoding, errors="ignore")
            from_stdout = from_stdout.replace('\r\n', '\n').replace('\r', '\n')
            trash_pos = from_stdout.find('pydev debugger:')
            if trash_pos >= 0:
                from_stdout = from_stdout[:trash_pos]
        return from_stdout, dur

    def _clean_up(self):
        # Удаляем старые тесты
        for filename in os.listdir(self.test_path):
            testname = filename
            if testname.endswith('.a'):
                testname = testname[:-2]
            if testname.isdigit():
                os.remove(os.path.join(_current_path, filename))

    @staticmethod
    def _list_test_files(path):
        """Find all files in given path which names contains only decimal digits.
        Such files are considered as test files.
        Result is sorted by int(test_name)"""
        test_files = [tname for tname in os.listdir(path)
                      if tname.isdecimal() and os.path.isfile(os.path.join(path, tname))]
        test_files.sort(key=lambda x: int(x))
        return test_files

    @staticmethod
    def _prc_text_for_console(text, is_binary=False, max_len=40):
        if is_binary:
            show_text = str(text[:max_len])[:max_len]
        else:
            show_text = text[:max_len]
        return show_text.replace('\r\n', '¶').replace('\n', '¶').replace('\r', '¶')

    @staticmethod
    def _cmp_two_outputs(output1, output2):
        eq = output1.rstrip() == output2.rstrip()
        return eq, ''

    @staticmethod
    def _read_test_or_ans(file_full_path, is_binary, encoding):
        open_parms = dict(file=file_full_path, mode='r')
        if is_binary:
            open_parms['mode'] = 'rb'
        else:
            open_parms['encoding'] = encoding
            open_parms['errors'] = "ignore"
        with open(**open_parms) as f:
            test_data = f.read()
        return test_data

    def _run_given_tests(self, test_files):
        for tname in test_files:
            lg.info('Processing test ' + tname + '...')

            # First we read the test
            try:
                test_data = self._read_test_or_ans(os.path.join(self.test_path, tname), self.test_is_binary, self.test_encoding)
            except Exception as e:
                lg.error('Error while reading test ' + tname + ': ' + str(e))
                continue
            # Then we read the result
            tname += self.res_suffix
            try:
                ans_data = self._read_test_or_ans(os.path.join(self.test_path, tname), self.res_is_binary, self.res_encoding)
            except Exception as e:
                lg.error('Error while reading test result for ' + tname + ': ' + str(e))
                continue

            # Ok, now we are ready to run pgm
            try:
                from_stdout, dur = self._run(to_stdin=test_data)
            except Exception as e:
                lg.error('Error while running test ' + tname + ': ' + str(e))
                continue

            show_test = self._prc_text_for_console(test_data, self.test_is_binary)
            show_res = self._prc_text_for_console(from_stdout, self.res_is_binary)
            show_ans = self._prc_text_for_console(ans_data, self.res_is_binary)

            eq, description = self._cmp_two_outputs(ans_data, from_stdout)
            msg = 'Test {}, {}. Dur:{:0.2f}.  {} -> {}  (Corr: {})'.format(tname, "OK" if eq else "WA", dur, show_test, show_res, show_ans)
            if eq:
                lg.info(msg)
            else:
                lg.error(msg)

    def compile_sol(self):
        self._compiled = None
        name, _, ext = self.solution.rpartition('.')
        ext = ext.lower()
        if ext == 'py':
            return
        elif ext == 'cpp':
            self._compiled = '{}.exe'.format(name)
            if os.path.isfile(self._compiled):
                os.remove(self._compiled)
            cmd = ' '.join([self.cpp_compiler, self.solution, '-o', self._compiled])
            if self.use_WSL:
                cmd = 'bash -c "{}"'.format(cmd)
            lg.debug(cmd)
            pr = subprocess.Popen(cmd,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  cwd=self.test_path)
            stdout, stderr = pr.communicate(timeout=self.compilation_timeout)
            lg.debug('stdout={}\nstderr={}'.format(stdout, stderr))
            if stderr:
                raise EnvironmentError(stderr.decode('utf-8', 'ignore'))

    def run_test(self):
        test_files = self._list_test_files(self.test_path)
        self._run_given_tests(test_files)

    def test(self, test, *, _test_num=[0], _max_len=40):
        test = test.strip()
        text_prt = self._prc_text_for_console(test, self.test_is_binary)
        _test_num[0] += 1
        _test_num_str = '{:03}'.format(_test_num[0])
        print('{}: {}{}    -->    '.format(_test_num_str, text_prt[:_max_len].ljust(_max_len),
                                           '...' if text_prt[_max_len:] else '   '), end='')

        ans, dur = self._run(test)
        ans_prt = self._prc_text_for_console(ans, self.res_is_binary)
        if dur <= self.timeout:
            print('{}{}  Done! {:.2}c'.format(ans_prt[:_max_len].ljust(_max_len),
                                              '...' if ans_prt[_max_len:] else '   ', dur))
            with open(_test_num_str, 'w') as f:
                f.write(test)
            with open(_test_num_str + '.a', 'w') as f:
                f.write(ans)
        else:
            print('timeout', '{:.2}c'.format(dur))


if __name__ == '__main__':
    # runner = TestRunner()
    # runner.run_test()
    print('sudo rm -rf, are you sure? Ok, type "password".')
