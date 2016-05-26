import os
import struct


_open = open


class ArInfo(object):
    def __init__(self, name, size=None,
                 mtime=None, perms=None, uid=None, gid=None):
        self.name = name
        self.size = size
        self.mtime = mtime
        self.perms = perms
        self.uid = uid
        self.gid = gid

    @classmethod
    def frombuffer(cls, buffer):
        # 0   16  File name                       ASCII
        # 16  12  File modification timestamp     Decimal
        # 28  6   Owner ID                        Decimal
        # 34  6   Group ID                        Decimal
        # 40  8   File mode                       Octal
        # 48  10  File size in bytes              Decimal
        # 58  2   File magic                      0x60 0x0A
        name, mtime, uid, gid, perms, size, magic = (
            struct.unpack('16s12s6s6s8s10s2s', buffer))
        mtime = int(mtime, 10)
        uid = int(uid, 10)
        gid = int(gid, 10)
        perms = int(perms, 8)
        size = int(size, 10)
        if magic != b'\x60\n':
            raise ValueError("Invalid file signature")
        return cls(name, size, mtime, perms, uid, gid)


class ArFile(object):
    def __init__(self, file, mode):
        self._file = file
        self._mode = mode
        if mode not in ('r', 'w'):
            raise ValueError("mode must be one of 'r' or 'w'")

        TODO

    def _check(self, expected_mode):
        if self._file is None:
            raise ValueError("Attempted to use a closed %s" %
                             self.__class__.__name__)
        if self._mode != expected_mode:
            if self._mode == 'r':
                raise ValueError("Can't change a read-only archive")
            else:
                raise ValueError("Can't read from a write-only archive")

    def add(self, name, arcname=None):
        self._check('w')
        TODO

    def addfile(self, name, fileobj=None):
        self._check('w')
        TODO

    def infolist(self):
        self._check('r')
        TODO

    def getinfo(self, member):
        self._check('r')
        TODO

    def extract(self, member, path=''):
        self._check('r')
        TODO

    def extractfile(self, member):
        self._check('r')
        TODO

    def extractall(self, path=''):
        self._check('r')
        TODO

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None


def open(file, mode):
    if hasattr(file, 'read'):
        return ArFile(file, mode)
    else:
        if mode == 'r':
            omode = 'rb'
        elif mode == 'w':
            omode = 'wb'
        else:
            raise ValueError("mode must be one of 'r' or 'w'")
        return ArFile(_open(file, omode), mode)
