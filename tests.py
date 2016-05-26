import unixar


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
