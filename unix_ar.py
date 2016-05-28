import os
import struct


_open = open


CHUNKSIZE = 4096


def utf8(s):
    if isinstance(s, bytes):
        return s
    else:
        return s.encode('utf-8')


class ArInfo(object):
    def __init__(self, name, size=None,
                 mtime=None, perms=None, uid=None, gid=None):
        self.name = name
        self.size = size
        self.mtime = mtime
        self.perms = perms
        self.uid = uid
        self.gid = gid
        self.offset = None

    def _name_set(self, value):
        self._name = utf8(value)

    name = property(lambda self: self._name, _name_set)

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
        name = utf8(name).rstrip(b' ')
        mtime = int(mtime, 10)
        uid = int(uid, 10)
        gid = int(gid, 10)
        perms = int(perms, 8)
        size = int(size, 10)
        if magic != b'\x60\n':
            raise ValueError("Invalid file signature")
        return cls(name, size, mtime, perms, uid, gid)

    def tobuffer(self):
        if any(f is None for f in (self._name, self.mtime,
                                   self.uid, self.gid, self.perms, self.size)):
            raise ValueError("ArInfo object has None fields")
        return (
            '{0: <16}{1: <12}{2: <6}{3: <6}{4: <8o}{5: <10}\x60\n'.format(
                self.name.decode('iso-8859-1'),
                self.mtime, self.uid, self.gid, self.perms, self.size)
            .encode('iso-8859-1'))

    def updatefromdisk(self, path=None):
        attrs = (
            self._name, self.size, self.mtime, self.perms, self.uid, self.gid)
        if not any(a is None for a in attrs):
            return self.__class__(*attrs)

        name, size, mtime, perms, uid, gid = attrs
        if path is None:
            path = name
        stat = os.stat(path)
        if name is None:
            name = utf8(path)
        if size is None:
            size = stat.st_size
        if mtime is None:
            mtime = int(stat.st_mtime)
        if perms is None:
            perms = stat.st_mode
        if uid is None:
            uid = stat.st_uid
        if gid is None:
            gid = stat.st_gid
        return self.__class__(name, size, mtime, perms, uid, gid)

    def __copy__(self):
        member = self.__class__(
            self._name, self.size, self.mtime, self.perms, self.uid, self.gid)
        member.offset = self.offset
        return member


class ArFile(object):
    def __init__(self, file, mode):
        self._file = file
        self._mode = mode
        if mode == 'r':
            self._read_entries()
        elif mode == 'w':
            self._file.write(b'!<arch>\n')
        else:
            raise ValueError("mode must be one of 'r' or 'w'")

    def _read_entries(self):
        if self._file.read(8) != b'!<arch>\n':
            raise ValueError("Invalid archive signature")

        self._entries = []
        self._name_map = {}
        pos = 8
        while True:
            buffer = self._file.read(60)
            if len(buffer) == 0:
                break
            elif len(buffer) == 60:
                member = ArInfo.frombuffer(buffer)
                member.offset = pos
                self._name_map[member.name] = len(self._entries)
                self._entries.append(member)
                skip = member.size
                if skip % 2 != 0:
                    skip += 1
                pos += 60 + skip
                self._file.seek(skip, 1)
                if pos == self._file.tell():
                    continue
            raise ValueError("Truncated archive?")

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
        if arcname is None:
            arcname = ArInfo(name)
        elif not isinstance(arcname, ArInfo):
            arcname = ArInfo(arcname)
        arcname = arcname.updatefromdisk(name)
        with _open(name, 'rb') as fp:
            self.addfile(arcname, fp)

    def addfile(self, name, fileobj=None):
        self._check('w')
        if not isinstance(name, ArInfo):
            name = ArInfo(name)

        name = name.updatefromdisk()

        self._file.write(name.tobuffer())
        if fileobj is None:
            fp = _open(name.name, 'rb')
        else:
            fp = fileobj

        for pos in range(0, name.size, CHUNKSIZE):
            chunk = fp.read(min(CHUNKSIZE, name.size - pos))
            if len(chunk) != CHUNKSIZE and len(chunk) != name.size - pos:
                raise RuntimeError("File changed size?")
            self._file.write(chunk)
        if name.size % 2 == 1:
            self._file.write(b'\n')

        if fileobj is None:
            fp.close()

    def infolist(self):
        self._check('r')
        return list(i.__copy__() for i in self._entries)

    def getinfo(self, member):
        self._check('r')
        if isinstance(member, ArInfo):
            if member.offset is not None:
                self._file.seek(member.offset, 0)
                return ArInfo.frombuffer(self._file.read(60))
            else:
                index = self._name_map[member.name]
                return self._entries[index].__copy__()
        else:
            index = self._name_map[utf8(member)]
            return self._entries[index].__copy__()

    def _extract(self, member, path):
        self._file.seek(member.offset + 60, 0)
        with _open(path, 'wb') as fp:
            for pos in range(0, member.size, CHUNKSIZE):
                chunk = self._file.read(min(CHUNKSIZE, member.size - pos))
                fp.write(chunk)

    def extract(self, member, path=''):
        self._check('r')
        actualmember = self.getinfo(member)
        if isinstance(member, ArInfo):
            if member.offset is None:
                member.offset = actualmember.offset
            if member.size > actualmember.size:
                member.size = actualmember.size
        else:
            member = actualmember
        if not path or os.path.isdir(path):
            path = os.path.join(utf8(path), member.name)
        self._extract(member, path)

    def extractfile(self, member):
        self._check('r')
        raise NotImplementedError("extractfile() is not yet implemented")

    def extractall(self, path=''):
        self._check('r')
        # Iterate on _name_map instead of plain _entries so we don't extract
        # multiple files with the same name, just the last one
        for index in self._name_map.values():
            member = self._entries[index]
            self._extract(member, os.path.join(utf8(path), member.name))

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
            self._entries = None
            self._name_map = None


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
