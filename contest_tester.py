# -*- coding: utf-8 -*-.
import subprocess
import os
import time
import sys
import logging
logging.basicConfig(level=logging.DEBUG)
lg = logging.getLogger('Runner')

__all__ = ['TestRunner']


_current_path = os.path.dirname(os.path.abspath(__file__))


class TestRunner:
    def __init__(self, test_path=_current_path,
                 executable=sys.executable, module_or_parm='sol.py',
                 test_encoding="utf-8", res_encoding="utf-8",
                 test_is_binary=False, res_is_binary=False,
                 res_suffix=".a", timeout=5):
        self.test_path = test_path
        self.executable = executable
        self.module_or_parm = module_or_parm
        self.test_encoding = test_encoding
        self.res_encoding = res_encoding
        self.test_is_binary = test_is_binary
        self.res_is_binary = res_is_binary
        self.res_suffix = res_suffix
        self.timeout = timeout
        os.chdir(test_path)

    def __repr__(self):
        return f'{self.__class__.__name__}(test_path={self.test_path!r}, executable={self.executable!r}, ' \
               f'module_or_parm={self.module_or_parm!r}, ' \
               f'test_encoding={self.test_encoding!r}, res_encoding={self.res_encoding!r}, ' \
               f'test_is_binary={self.test_is_binary!r}, res_is_binary={self.res_is_binary!r}, ' \
               f'res_suffix={self.res_suffix!r}), timeout={self.timeout!r})'

    def _run(self, to_stdin):
        if self.test_is_binary:
            input = to_stdin
        else:
            input = bytes(to_stdin, encoding=self.test_encoding)
        st = time.time()
        pr = subprocess.Popen([self.executable, self.module_or_parm],
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
            msg = f'Test {tname}, {"OK" if eq else "WA"}. Dur:{dur:0.2f}.  {show_test} -> {show_res}  (Corr: {show_ans})'
            if eq:
                lg.info(msg)
            else:
                lg.error(msg)

    def run_test(self):
        test_files = self._list_test_files(self.test_path)
        self._run_given_tests(test_files)


if __name__ == '__main__':
    runner = TestRunner()
    runner.run_test()
