import os
import platform
import sqlite3
import sys
import tempfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ej_test_gen import TestRunner


def write_solution(tmp_path, code):
    sol = tmp_path / 'sol.py'
    sol.write_text(code, encoding='utf-8')
    return str(sol)


def get_input_files(tmp_path):
    """Return sorted list of test input files (names are all digits)."""
    files = [f for f in tmp_path.iterdir() if f.name.isdecimal()]
    return sorted(files, key=lambda f: int(f.name))


def get_answer_file(input_file):
    return input_file.parent / (input_file.name + '.a')


# ---------------------------------------------------------------------------
# Text input / text output
# ---------------------------------------------------------------------------

class TestTextIO:
    def test_echo(self, tmp_path):
        sol = write_solution(tmp_path, "print(input())")
        runner = TestRunner(solution=sol, tests_path=str(tmp_path))
        runner.test('hello')

        inputs = get_input_files(tmp_path)
        assert len(inputs) == 1
        assert inputs[0].read_text(encoding='utf-8') == 'hello'
        assert get_answer_file(inputs[0]).read_text(encoding='utf-8').strip() == 'hello'

    def test_arithmetic(self, tmp_path):
        sol = write_solution(tmp_path, "a, b = map(int, input().split()); print(a + b)")
        runner = TestRunner(solution=sol, tests_path=str(tmp_path))
        runner.test('3 4')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text(encoding='utf-8').strip() == '7'

    def test_multiple_tests(self, tmp_path):
        sol = write_solution(tmp_path, "print(int(input()) * 2)")
        runner = TestRunner(solution=sol, tests_path=str(tmp_path))
        runner.test('3')
        runner.test('5')

        inputs = get_input_files(tmp_path)
        assert len(inputs) == 2
        answers = [get_answer_file(f).read_text().strip() for f in inputs]
        assert answers == ['6', '10']


# ---------------------------------------------------------------------------
# Binary input / text output
# ---------------------------------------------------------------------------

class TestBinaryInput:
    def test_binary_stdin_byte_count(self, tmp_path):
        """Binary input (arbitrary bytes) → text output: length of data."""
        code = "import sys; data = sys.stdin.buffer.read(); print(len(data))"
        sol = write_solution(tmp_path, code)
        binary_data = bytes(range(256))

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=False,
        )
        runner.test(binary_data)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == binary_data
        assert get_answer_file(inputs[0]).read_text().strip() == '256'

    def test_binary_stdin_null_bytes(self, tmp_path):
        """Binary input containing null bytes (common in binary files)."""
        code = "import sys; d = sys.stdin.buffer.read(); print(d.count(0))"
        sol = write_solution(tmp_path, code)
        binary_data = bytes([0x00, 0x01, 0x00, 0xFF, 0x00])  # three null bytes

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=False,
        )
        runner.test(binary_data)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == binary_data
        assert get_answer_file(inputs[0]).read_text().strip() == '3'

    def test_sqlite_database_input(self, tmp_path):
        """Binary input is a SQLite database file."""
        # Build a tiny DB
        db_path = tmp_path / 'input.db'
        conn = sqlite3.connect(str(db_path))
        conn.execute('CREATE TABLE nums (val INTEGER)')
        conn.execute('INSERT INTO nums VALUES (42)')
        conn.commit()
        conn.close()
        db_bytes = db_path.read_bytes()

        code = '''
import sys, sqlite3, tempfile, os
data = sys.stdin.buffer.read()
with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
    f.write(data)
    fname = f.name
conn = sqlite3.connect(fname)
row = conn.execute('SELECT val FROM nums').fetchone()
conn.close()
os.unlink(fname)
print(row[0])
'''
        sol = write_solution(tmp_path, code)
        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=False,
        )
        runner.test(db_bytes)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == db_bytes
        assert get_answer_file(inputs[0]).read_text().strip() == '42'


# ---------------------------------------------------------------------------
# Text input / binary output
# ---------------------------------------------------------------------------

class TestBinaryOutput:
    def test_text_in_binary_out(self, tmp_path):
        """Text input → binary output: emit n sequential bytes."""
        code = "import sys; n = int(input()); sys.stdout.buffer.write(bytes(range(n)))"
        sol = write_solution(tmp_path, code)

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=False,
            ans_is_binary=True,
        )
        runner.test('5')

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_text().strip() == '5'
        assert get_answer_file(inputs[0]).read_bytes() == bytes(range(5))

    def test_text_in_binary_out_with_nulls(self, tmp_path):
        """Binary output must preserve null bytes."""
        code = "import sys; sys.stdout.buffer.write(bytes([0, 1, 0, 2, 0]))"
        sol = write_solution(tmp_path, code)

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=False,
            ans_is_binary=True,
        )
        runner.test('ignored')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_bytes() == bytes([0, 1, 0, 2, 0])


# ---------------------------------------------------------------------------
# Binary input / binary output
# ---------------------------------------------------------------------------

class TestBinaryInputOutput:
    def test_invert_bytes(self, tmp_path):
        """Binary in/out: bitwise invert every byte."""
        code = "import sys; d = sys.stdin.buffer.read(); sys.stdout.buffer.write(bytes(b ^ 0xFF for b in d))"
        sol = write_solution(tmp_path, code)

        input_bytes = bytes([0x00, 0xFF, 0xAA, 0x55])
        expected = bytes([0xFF, 0x00, 0x55, 0xAA])

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=True,
        )
        runner.test(input_bytes)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == input_bytes
        assert get_answer_file(inputs[0]).read_bytes() == expected

    def test_image_like_binary(self, tmp_path):
        """Binary in/out: strip first 8 bytes (simulate PNG header extraction)."""
        png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
        input_bytes = png_header + bytes(range(100))

        code = "import sys; d = sys.stdin.buffer.read(); sys.stdout.buffer.write(d[:8])"
        sol = write_solution(tmp_path, code)

        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=True,
        )
        runner.test(input_bytes)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == input_bytes
        assert get_answer_file(inputs[0]).read_bytes() == png_header

    def test_binary_passthrough_large(self, tmp_path):
        """Binary in/out: 1 KB of non-whitespace bytes are faithfully preserved."""
        # Avoid trailing whitespace bytes (0x00–0x08, 0x0e–0x1f, 0x21–0xff are safe)
        input_bytes = bytes([((i * 7 + 33) % 223) + 33 for i in range(1024)])
        code = "import sys; sys.stdout.buffer.write(sys.stdin.buffer.read())"
        sol = write_solution(tmp_path, code)
        runner = TestRunner(
            solution=sol,
            tests_path=str(tmp_path),
            test_is_binary=True,
            ans_is_binary=True,
        )
        runner.test(input_bytes)

        inputs = get_input_files(tmp_path)
        assert inputs[0].read_bytes() == input_bytes
        assert get_answer_file(inputs[0]).read_bytes() == input_bytes


# ---------------------------------------------------------------------------
# use_WSL=True ignored on non-Windows
# ---------------------------------------------------------------------------

class TestWSLOnNonWindows:
    def test_use_wsl_ignored(self, tmp_path):
        """use_WSL=True must not crash or break execution on non-Windows."""
        if platform.system() == 'Windows':
            pytest.skip('WSL is meaningful on Windows; skip non-Windows check')

        sol = write_solution(tmp_path, "print(int(input()) + 1)")
        runner = TestRunner(solution=sol, tests_path=str(tmp_path), use_WSL=True)
        runner.test('41')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text().strip() == '42'

    def test_compile_sol_use_wsl_ignored(self, tmp_path):
        """compile_sol() must not crash with use_WSL=True on non-Windows."""
        if platform.system() == 'Windows':
            pytest.skip('WSL is meaningful on Windows; skip non-Windows check')

        # A Python solution — compile_sol() returns early for .py, but the
        # TestRunner constructor must succeed without errors.
        sol = write_solution(tmp_path, "print('ok')")
        runner = TestRunner(solution=sol, tests_path=str(tmp_path), use_WSL=True)
        runner.test('x')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text().strip() == 'ok'
