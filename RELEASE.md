# Release procedure

## Pre-requisites

- Must have push rights to the GitHub repository
- Must be a maintainer or owner of the project on PyPI
- Must have valid PyPI credentials in `~/.pypirc`
- Should be a maintainer of the project on ReadTheDocs

## Release

1. Update version number in [`mosromgr/__init__.py`](mosromgr/__init__.py)

1. Update changelog with summary of changes in [`docs/changelog.rst`](docs/changelog.rst)

1. Ensure all code changes are reflected in the documentation and that the
documentation builds correctly (`make doc`)

1. Commit final changes and tag with the version number:

    ```bash
    git tag -a v0.8.1 -m v0.8.1
    ```

1. Push to GitHub, including tags:

    ```bash
    git push
    git push --tags
    ```

1. Run `make build` to create source and binary distributions

1. Run `make release` to release source and binary distribution files to PyPI

1. ReadTheDocs should build the new version automatically if the connection to
GitHub is active. Verify and login to check status if needed. There should be a
new version available, and the `stable` branch of the docs should now reflect
the new release.

## Bus factor

GitHub owners:

- BBC / News Labs team

PyPI owners:

- Ben Nuttall
- Nik Rahmel

ReadTheDocs owners:

- Ben Nuttall
- Nik Rahmel
