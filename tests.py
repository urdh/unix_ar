import os
import shutil
import tempfile

import unixar

try:
    import unittest2 as unittest
except ImportError:
    import unittest


class TestWrite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._dir = tempfile.mkdtemp(prefix='unixar_test_')
        os.chdir(cls._dir)
        with open('h.txt', 'wb') as fp:
            fp.write(b'hello,\n')
        with open('w.txt', 'wb') as fp:
            fp.write(b'world\n')

    @classmethod
    def tearDownClass(cls):
        os.chdir('/')
        shutil.rmtree(cls._dir)

    def assertEqualExceptTwos(self, value, expected):
        if len(value) != len(expected):
            raise AssertionError("%r != %r (lengths don't match)" % (
                                 value, expected))
        two = b'2'[0]  # PY3 workaround
        for i, (v, e) in enumerate(zip(value, expected)):
            if e != two and v != e:
                raise AssertionError("%r != %r (first mismatch at %d)" % (
                                     value, expected, i))

    def test_empty(self):
        archive = unixar.open('empty.ar', 'w')
        archive.close()

        with open('empty.ar', 'rb') as fp:
            self.assertEqual(fp.read(),
                             b'!<arch>\n')

    def test_add(self):
        archive = unixar.open('add.ar', 'w')
        archive.add('h.txt', arcname='he')
        archive.add('w.txt')
        archive.close()

        with open('add.ar', 'rb') as fp:
            self.assertEqualExceptTwos(
                fp.read(),
                b'!<arch>\n'
                b'he              2222222222  2222  '
                b'2222  100622  7         `\n'
                b'hello,\n'
                b'\n'
                b'w.txt           2222222222  2222  '
                b'2222  100622  6         `\n'
                b'world\n')

    def test_addfile(self):
        archive = unixar.open('addfile.ar', 'w')
        with open('w.txt', 'rb') as fp:
            archive.addfile(unixar.ArInfo('w.txt', size=4), fp)
        with open('h.txt', 'rb') as fp:
            archive.addfile('w.txt', fp)
        archive.close()

        with open('addfile.ar', 'rb') as fp:
            self.assertEqualExceptTwos(
                fp.read(),
                b'!<arch>\n'
                b'w.txt           2222222222  2222  '
                b'2222  100622  4         `\n'
                b'worl'
                b'w.txt           2222222222  2222  '
                b'2222  100622  6         `\n'
                b'hello,')


def main():
    archive = unixar.open('/tmp/test.ar', 'w')

    archive.add('/tmp/h.txt', arcname='h.txt')
    archive.addfile(unixar.ArInfo('w.txt'), open('/tmp/w.txt', 'rb'))

    archive.close()


    archive = unixar.open('/tmp/test.ar', 'r')

    archive.infolist()
    archive.getinfo('h.txt')

    archive.extract('h.txt')
    archive.extractfile('w.txt')
    archive.extractall()

    archive.close()


if __name__ == '__main__':
    unittest.main()
