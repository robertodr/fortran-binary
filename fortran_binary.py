"""
    This module defines a class FortranBinary for reading binary 
    files generated by FORTRAN unformatted I/O
"""
__version__ = "1.0"
import struct

class FortranBinary(object):
    """Class for binary files compatible with Fortran Unformatted I/O"""

    pad = 4

    def __init__(self, name, mode="rb"):
        self.name = name
        self.file = open(name, mode)
        self.data = None
        self.rec = None

    @property
    def reclen(self):
        return self.rec.reclen

    def __iter__(self):
        return self

    def __next__(self): #pragma: no cover
        return self.next()

    def next(self):
        """Read a Fortran record"""
        head = self.file.read(self.pad)
        if head:
            record_size = struct.unpack('i', head)[0]
            self.data = self.file.read(record_size)
            tail = self.file.read(self.pad)
            assert head == tail
            self.rec = Rec(self.data)
            return self.rec
        else:
            raise StopIteration

    def readbuf(self, num, fmt):
        """Read data from current record"""
        vec = self.rec.read(num, fmt)
        return vec

    def find(self, label):
        """Find string label in file"""
        if isinstance(label, str):
            try:
                blabel = bytes(label, 'utf-8')
            except TypeError:
                blabel = label
        elif isinstance(label, bytes):
            blabel = label
        else:
            raise ValueError

        for rec in self:
            if blabel in rec:
                return rec

    def record_byte_lengths(self):
        """Return record byte lengths in file as tuple"""

        reclengths = [record.reclen for record in self]
        return tuple(reclengths)

    def __enter__(self, *args, **kwargs):
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __getattr__(self, attr):
        """Delegate unknown attributes to file member"""
        return getattr(self.file, attr)

class Rec(object):
    """Representation of a single Fortran record"""

    def __init__(self, data):
        self.data = data
        self.loc = 0

    def __contains__(self, obj):
        return obj in self.data

    @property
    def reclen(self):
        return len(self.data)

    def read(self, num, fmt):
        """Read data from current record"""
        start, stop = self.loc, self.loc+struct.calcsize(fmt*num)
        vec = struct.unpack(fmt*num, self.data[start:stop])
        self.loc = stop
        return vec

def main():
    import argparse 

    parser = argparse.ArgumentParser()
    parser.add_argument('--records', action='store_true', help='List record lengths')
    parser.add_argument('filename', help='Fortran binary flie')
    args = parser.parse_args()

    if args.records:
        file_ = FortranBinary(args.filename)
        print(file_.record_byte_lengths())

if __name__ == "__main__": #pragma: no cover
    pass
