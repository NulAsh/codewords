import sys
import lzma
import pickle
import bitstring

if (len(sys.argv) < 4) or (sys.argv[1] not in ('-e', '-d')):
    print('Syntax to encode:')
    print('    codewords.py -e infile outfile')
    print('Syntax to decode:')
    print('    codewords.py -d infile outfile')
    sys.exit(1)
d = lzma.open('codes8.bin', 'rb', format=lzma.FORMAT_RAW, filters=[{"id": lzma.FILTER_LZMA2, "preset": 9 | lzma.PRESET_EXTREME}]).read()
num2word = pickle.loads(d[:3277525])
word2num = pickle.loads(d[3277525:])

def encode():
    st = bitstring.ConstBitStream(filename=sys.argv[2])
    f2 = open(sys.argv[3], 'w')
    first_code = True
    def write_b(b):
        nonlocal first_code
        nonlocal f2
        if first_code:
            f2.write(b)
            first_code = False
        else:
            f2.write(' ' + b)
    while True:
        try:
            a = st.read(18).uint
            b = num2word[a]
            write_b(b)
        except bitstring.ReadError:
            tail = st[st.pos:] + '0b1'
            if tail.len < 18:
                tail += bitstring.Bits(18 - tail.len)
            b = num2word[tail.uint]
            write_b(b)
            break
    f2.close()

def decode():
    f1 = open(sys.argv[2], 'r', encoding='latin1')
    f2 = open(sys.argv[3], 'wb')
    st = bitstring.BitArray()
    cw = ''
    while True:
        buf = f1.read(512)
        for c in buf:
            b = ord(c.upper())
            if (b >= ord('A')) and (b <= ord('Z')):
                cw += c.upper()
                if len(cw) == 5:
                    if cw not in word2num:
                        print('Wrong codeword: ' + cw)
                        exit(2)
                    if st.len >= 4096:
                        st[:4096].tofile(f2)
                        del st[:4096]
                    st.append(bitstring.Bits(uint=word2num[cw], length=18))
                    cw = ''
        if len(buf) != 512:
            break
    st[:st.rfind('0b1')[0]].tofile(f2)
    f1.close()
    f2.close()

if sys.argv[1] == '-e':
    encode()
elif sys.argv[1] == '-d':
    decode()