![Test suite](https://github.com/bbc/mosromgr/workflows/Run%20test%20suite/badge.svg)

# mosromgr

Python library for managing [MOS](http://mosprotocol.com/) running orders.

[![](docs/images/mos.jpg)](http://mosprotocol.com/)

The library provides functionality for detecting MOS file types, merging MOS
files into a running order, and providing a "completed" programme including all
additions and changes made between the first message (`roCreate`) and the last
(`roDelete`).

This can be used as a library, using the utilities provided in the module
**mosromgr**, and the command line command `mosromgr` can be used to process
either a directory of MOS files, or a folder within an S3 bucket.

This library was developed by the [BBC News Labs](https://bbcnewslabs.co.uk/)
team.

## Usage

### Command line

Merge all MOS files in directory `dirname`:

```bash
mosromgr -d dirname
```

Merge all MOS files in S3 folder `prefix` in bucket `bucketname`:

```bash
mosromgr -b bucketname -p prefix
```

The final running order is output to stdout, so to save to a file use `>` e.g:

```bash
mosromgr -d dirname > FINAL.xml
```

### Library

Simple example merging a single `roStorySend` into a `roCreate` and outputting
the file to a new file:

```python
from mosromgr.mostypes import RunningOrder, StorySend

ro = RunningOrder('roCreate.mos.xml')
ss = StorySend('roStorySend.mos.xml')

ro += ss

with open('final.mos.xml', 'w') as f:
    f.write(ro)
```

Alternatively, use `MosContainer` which will sort and classify MOS types of all
given files:

```python
from mosromgr.moscontainer import MosContainer

mos_files = ['roCreate.mos.xml', 'roStorySend.mos.xml', 'roDelete.mos.xml']
mc = MosContainer(mos_files)

mc.merge()
with open('final.mos.xml', 'w') as f:
    f.write(mc)
```

## Development

### Dependencies

- Python 3.6+
- boto3

Test dependencies:

- pytest
- coverage
- mock
- xmltodict

Docs:

- graphviz
- sphinx

The makefile will deal with Python dependencies, but you'll need to install
graphviz yourself to build the docs graphs.

### Local

1. Create a virtualenv, e.g using [virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/):

    ```bash
    mkvirtualenv -p /usr/bin/python3 mosromgr
    ```

    (this will activate automatically - to re-activate, run `workon mosromgr`)

1. Run `make develop`:

    ```bash
    make develop
    ```

This should install the library and its full dependencies, and install the
`mosromgr` command line utility.

### Tests

To run the tests locally:

```bash
make test
```

Tests are configured to run on push/PR via GitHub Action.

### Documentation

Live documentation can be found at https://apps.test.newslabs.co/docs/mosromgr
which requires BBC Login.

To build the docs:

```bash
make doc
```

To serve the docs locally:

```bash
make doc-serve
```

To deploy the docs:

```bash
make doc-deploy
```

## Contributing

Source code can be found on GitHub at https://github.com/bbc/mosromgr which
also hosts the [issue tracker](https://github.com/bbc/mosromgr/issues) and
[contributing guidelines](https://github.com/bbc/mosromgr/blob/main/.github/CONTRIBUTING.md).

## Contributors

- [Ben Nuttall](https://github.com/bennuttall)
- [Owen Tourlamain](https://github.com/OwenTourlamain)
- [Rob French](https://github.com/FrencR)

## Licence

TBC

## Contact

Please contact the BBC News Labs team (`BBCNewsLabsTeam@bbc.co.uk`) if you want
to get in touch.
