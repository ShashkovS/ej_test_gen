# Library development and runtime boundary

The shared workspace deliberately uses PyPI 0.4.1. This independent checkout can change without changing that installed runtime, even if its version string is unchanged.

Read this when editing the library, running its tests or discussing a release.

Use this repository's `.venv` and its declared development dependencies. Run
`.venv/bin/python -m pytest` from this repository. The committed tests explicitly import
the checkout's `src`, so passing them proves source behaviour, not a republished PyPI
artifact. Do not swap the shared root package for an editable checkout to make it pass.

Before relying on new behaviour in a course generator, identify the actual interpreter,
import location and installed release. A source commit, package version label and
published artifact are separate evidence. A runtime upgrade/release is an explicit
separate change; documentation migration does not publish it or reinstall environments.

Keep experiments and generated numeric tests in scratch: construction/generation cleans
its chosen output directory. Test source changes with the existing Python/C++ path,
wrapper, error and normalization cases. Inspect binary bytes separately from console
previews; a display that looks right is not proof the `.a` file is correct.
