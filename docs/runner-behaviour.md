# Runner behaviour and destructive output scope

The runner resolves paths from an explicit base and replaces numeric output files. These choices make scripts portable but require deliberate output-directory selection.

Read this when choosing working_dir, wrapping, output modes or error handling.

## Paths and cleanup

When `working_dir` is omitted, relative solution/tests/header/footer paths are based
on the **creating script's directory**, not the process cwd. Explicit `working_dir="."`
retains cwd-relative behaviour. Default `tests_dir="."` can put numeric files beside
the generator; course packages normally use `tests_dir="tests"`.

The runner removes old numeric inputs and `.a` answers in its output directory and
recompiles C++ references. Inspect the resolved directory before running; use scratch
for library experiments rather than a real course test tree.

## Wrappers and bytes

Use header/footer files to match what judge compilation appends, instead of duplicating
call/print logic in the model function. Keep a portable C++ source and a warning-clean
compile: compiler stderr is treated as failure. The course authoring skill owns reference
style and test-design philosophy, not this library page.

Text inputs/answers are normalized with final newlines; binary flags preserve bytes.
Choose the corresponding encoding/binary mode and compare actual output files. A
picture/WAV payload is not text to be stripped or newline-normalized.

## Errors

`on_error="default"` stops/raises on nonzero exit or stderr. `ignore` skips failed tests;
`output` writes diagnostics into the answer. That last mode is useful for investigation,
not a valid normal model answer. Old `raise`/`skip` names remain aliases.
Timeout applies to the reference run; raise it only deliberately, not to hide a package
whose model cannot answer its own maximum case.

These are checkout semantics. [Runtime/release verification](development.md) is required
before assuming the shared PyPI installation has a newly changed implementation.
