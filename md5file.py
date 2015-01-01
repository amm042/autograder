import hashlib
def hashfile(afile, hasher, blocksize=64*1024):
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.digest()

if __name__ == "__main__":
    print ([hashfile(open(fname, 'rb'), hashlib.md5()) for fname in ['hello.c']])
