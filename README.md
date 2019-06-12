unix_ar
=======

[![PyPI version fury.io](https://badge.fury.io/py/unix_ar.svg)](https://pypi.python.org/pypi/unix_ar/)
[![Build Status](https://travis-ci.org/getninjas/unix_ar.svg?branch=master)](https://travis-ci.org/getninjas/unix_ar)
[![Read The Docs](https://readthedocs.org/projects/unix_ar/badge/?version=latest)](https://unix_ar.readthedocs.io/en/latest/?badge=latest)


This packages allows the reading and writing of [`AR archive files`](https://en.wikipedia.org/wiki/Ar_(Unix)).

It is inspired by the `tarfile` and `zipfile` that are part of Python's standard library (unfortunately the name ``arfile`` was taken on PyPI).


Features
--------

The package provides a `ArFile` partially implementing the interface of
[`tarfile.TarFile`](https://docs.python.org/3/library/tarfile.html#tarfile-objects)

```python
>>> import unix_ar
>>> import tarfile
>>> ar_file = unix_ar.open('mypackage.deb')
>>> tarball = ar_file.open('data.tar.gz/')  # default interest location on .deb files
>>> tar_file = tarfile.open(fileobj=tarball)  # handles gz decompression internally
>>> tar_file.extractfile('usr/local/mypackage/bin/mybinarycontent.sh')
```

Credits
-------

This package was created by Remi Rampin, that does not want to maintain it anymore.
