# ej_test_gen

Generator library source. The shared CSTLF runtime deliberately uses PyPI
0.4.1; changing this checkout does not change that installation.

## Development (from this repository)

Use this independent repo's Python environment: `.venv/bin/python -m pytest`.
The tests explicitly import the checkout's source. Do not replace the shared
workspace installation with an editable checkout to make a test pass.

## Invariants and gotchas

- Default relative paths are based on the creating script's directory;
  explicit `working_dir="."` uses the process working directory.
- Generation cleans old numeric tests in its target directory; use scratch for experiments.
- Text files receive final newlines; binary input/output remains byte-exact.
- Keep header/footer wrapping consistent with judge compilation.
- Error handling may stop, skip or emit diagnostics into an answer; choose
  deliberately, because a diagnostic answer is unsuitable for a normal package.
- Source and PyPI releases may differ despite the same version string.

## Read when

| Task | Document |
|---|---|
| Change library behaviour or release assumptions | `docs/development.md` |
| Understand paths, cleanup, wrapping and errors | `docs/runner-behaviour.md` |
| Build a course package | skill `cstlf-tests` or `cstlf-tests-olymp` |

Docs are part of every change: update the owning page and its row above in the
same commit, and put durable facts here rather than in an agent's memory
(workspace map, "Documentation is part of the change").
