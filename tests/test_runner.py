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
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))
        runner.test('hello')

        inputs = get_input_files(tmp_path)
        assert len(inputs) == 1
        assert inputs[0].read_text(encoding='utf-8') == 'hello'
        assert get_answer_file(inputs[0]).read_text(encoding='utf-8').strip() == 'hello'

    def test_arithmetic(self, tmp_path):
        sol = write_solution(tmp_path, "a, b = map(int, input().split()); print(a + b)")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))
        runner.test('3 4')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text(encoding='utf-8').strip() == '7'

    def test_multiple_tests(self, tmp_path):
        sol = write_solution(tmp_path, "print(int(input()) * 2)")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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
            working_dir=str(tmp_path),
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

# ---------------------------------------------------------------------------
# tests_dir
# ---------------------------------------------------------------------------

class TestTestsDir:
    def test_default_tests_dir_equals_tests_path(self, tmp_path):
        """Default tests_dir='.' stores files directly in tests_path."""
        sol = write_solution(tmp_path, "print(int(input()) + 1)")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))
        runner.test('9')

        inputs = get_input_files(tmp_path)
        assert len(inputs) == 1
        assert get_answer_file(inputs[0]).read_text().strip() == '10'

    def test_relative_tests_dir_created_automatically(self, tmp_path):
        """Relative tests_dir is created under tests_path automatically."""
        sol = write_solution(tmp_path, "print(int(input()) * 3)")
        subdir = tmp_path / 'generated'
        assert not subdir.exists()

        runner = TestRunner(solution=sol, working_dir=str(tmp_path), tests_dir='generated')
        assert subdir.exists()

        runner.test('7')
        inputs = get_input_files(subdir)
        assert len(inputs) == 1
        assert get_answer_file(inputs[0]).read_text().strip() == '21'
        # Root tests_path must stay clean of test files
        assert get_input_files(tmp_path) == []

    def test_nested_relative_tests_dir_created(self, tmp_path):
        """Multi-level relative tests_dir is created with makedirs."""
        sol = write_solution(tmp_path, "print('hi')")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), tests_dir='a/b/c')
        nested = tmp_path / 'a' / 'b' / 'c'
        assert nested.exists()

        runner.test('x')
        assert len(get_input_files(nested)) == 1

    def test_absolute_tests_dir(self, tmp_path):
        """Absolute tests_dir path is used as-is regardless of tests_path."""
        sol_dir = tmp_path / 'sol'
        sol_dir.mkdir()
        out_dir = tmp_path / 'out'
        # out_dir does not exist yet

        sol = write_solution(sol_dir, "print(42)")
        runner = TestRunner(
            solution=str(sol),
            working_dir=str(sol_dir),
            tests_dir=str(out_dir),  # absolute
        )
        assert out_dir.exists()

        runner.test('ignored')
        assert len(get_input_files(out_dir)) == 1
        assert get_input_files(sol_dir) == []

    def test_existing_tests_dir_ok(self, tmp_path):
        """If tests_dir already exists, no error is raised."""
        subdir = tmp_path / 'tests'
        subdir.mkdir()
        sol = write_solution(tmp_path, "print('x')")
        # Should not raise even though the directory exists
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), tests_dir='tests')
        runner.test('y')
        assert len(get_input_files(subdir)) == 1

    def test_cleanup_only_affects_tests_dir(self, tmp_path):
        """_clean_up removes old test files only from tests_dir, not tests_path root."""
        sol = write_solution(tmp_path, "print('ok')")
        subdir = tmp_path / 'tests'

        # Pre-populate tests_dir with stale test files
        subdir.mkdir()
        (subdir / '01').write_text('old input')
        (subdir / '01.a').write_text('old answer')

        runner = TestRunner(solution=sol, working_dir=str(tmp_path), tests_dir='tests')
        # _clean_up is called in __init__; stale files should be gone
        assert not (subdir / '01').exists()
        assert not (subdir / '01.a').exists()


# ---------------------------------------------------------------------------
# on_error behaviour
# ---------------------------------------------------------------------------

class TestOnError:
    def test_raise_on_nonzero_exit(self, tmp_path):
        """on_error='raise' (default) raises RuntimeError on non-zero returncode."""
        sol = write_solution(tmp_path, "raise ValueError('boom')")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))

        with pytest.raises(RuntimeError, match='returncode'):
            runner.test('anything')

    def test_raise_on_stderr(self, tmp_path):
        """on_error='raise' raises RuntimeError when solution writes to stderr."""
        code = "import sys; sys.stderr.write('oops\\n'); print('ok')"
        sol = write_solution(tmp_path, code)
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))

        with pytest.raises(RuntimeError):
            runner.test('anything')

    def test_raise_no_files_created(self, tmp_path):
        """When on_error='raise', no test files are written before the exception."""
        sol = write_solution(tmp_path, "raise RuntimeError('x')")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path))

        with pytest.raises(RuntimeError):
            runner.test('x')

        assert get_input_files(tmp_path) == []

    def test_skip_on_nonzero_exit(self, tmp_path):
        """on_error='skip' silently skips tests where solution crashes."""
        sol = write_solution(tmp_path, "raise ValueError('boom')")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), on_error='skip')

        # Must not raise
        runner.test('anything')
        assert get_input_files(tmp_path) == []

    def test_skip_does_not_advance_counter(self, tmp_path):
        """Skipped tests don't consume a test number slot."""
        code = """\
import sys
n = int(input())
if n < 0:
    raise ValueError('negative')
print(n * 2)
"""
        sol = write_solution(tmp_path, code)
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), on_error='skip')

        runner.test('3')   # succeeds → file '01' (or some N)
        runner.test('-1')  # crashes  → skipped, counter not advanced
        runner.test('5')   # succeeds → file 'N+1'

        inputs = get_input_files(tmp_path)
        assert len(inputs) == 2
        answers = [get_answer_file(f).read_text().strip() for f in inputs]
        assert answers == ['6', '10']
        # The two files must be consecutive
        nums = [int(f.name) for f in inputs]
        assert nums[1] == nums[0] + 1

    def test_skip_on_stderr(self, tmp_path):
        """on_error='skip' skips tests that produce stderr output."""
        code = "import sys; sys.stderr.write('warn\\n'); print('result')"
        sol = write_solution(tmp_path, code)
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), on_error='skip')

        runner.test('x')
        assert get_input_files(tmp_path) == []

    def test_clean_run_not_affected(self, tmp_path):
        """on_error='raise' must not interfere with completely clean solutions."""
        sol = write_solution(tmp_path, "print(input()[::-1])")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), on_error='raise')

        runner.test('abc')
        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text().strip() == 'cba'


# ---------------------------------------------------------------------------
# use_WSL=True ignored on non-Windows
# ---------------------------------------------------------------------------

class TestWSLOnNonWindows:
    def test_use_wsl_ignored(self, tmp_path):
        """use_WSL=True must not crash or break execution on non-Windows."""
        if platform.system() == 'Windows':
            pytest.skip('WSL is meaningful on Windows; skip non-Windows check')

        sol = write_solution(tmp_path, "print(int(input()) + 1)")
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), use_WSL=True)
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
        runner = TestRunner(solution=sol, working_dir=str(tmp_path), use_WSL=True)
        runner.test('x')

        inputs = get_input_files(tmp_path)
        assert get_answer_file(inputs[0]).read_text().strip() == 'ok'
