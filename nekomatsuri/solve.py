key2 = b'\xA6\x68\x19\xB0\x94\x8F\x5F\xA1\x8B\x20\x0D\x54\x3B\xF7\x57\x3C'
key1 = b'WinExec'
key0 = b'\x8F\xE6\xC7\x84'

encflag = b'\x1C\xF5\x9E\x13\x7F\x21\xC5\x0D\x15\x3A\xE6\xF8\xA7\x9E\x9F\xEC\x56\x6D\xF8\x2C\xF0\x80\xA6\x96\x04\x8C\xB9\x6F\x8B\xCC\x74\x43\x3A\xA1\x07\x10\x55\x47\xD2\x96\x36\x9D\x8E\x6B\x84\x89\x7E\xC4\x63\xE6\x61\x9B\x7A\xD7\xAD\x32\xAD\x82\x4A\x67\x04\x7E\x32\xCA\x74'
arg1 = b'Ch1y0d4m0m0'
wrong = b'\x4A\xA6\x43\x80\x57\x2E\xEC\x6C\x7A'
kernel = b'\xD8\x47\x8E\x00\x37\x9B\x6F\x95\xA6\x85\x12\x54\x85'

kernel = bytearray(kernel)
encflag = bytearray(encflag)

key2 = bytearray(key2)
key1 = bytearray(key1)
key0 = bytearray(key0)

def decryption(mystring, slen, key, klen, constant):
    unicode = []

    for i in range(256):
        unicode.append(i)

    v14 = 0

    for j in range(256):
        v14 += (unicode[j] + key[j % klen])
        v14 &= 0xff
        unicode[j] ^= unicode[v14]
        unicode[v14] ^= unicode[j]
        unicode[j] ^= unicode[v14]

    v14 = 0

    for k in range(slen):
        v9 = unicode[k + 1]
        v14 += v9
        v14 &= 0xff

        unicode[k+1] ^= unicode[v14]
        unicode[v14] ^= unicode[k+1]
        unicode[k+1] ^= unicode[v14]

        v8 = (unicode[k+1] + v9) & 0xff
        v7 = unicode[v8] & 0xff

        if ( constant & 0x80 ):
            mystring[k] = ((v7 ^ mystring[k]) + constant) & 0xff
        else:
            mystring[k] = (v7 ^ (mystring[k] + constant)) & 0xff


decryption(key2, 16, key1, 7, 253) # 253
decryption(encflag, 65, key2, 16, 30)

for i in range(65):
    encflag[i] =  encflag[i] ^ (i ^ arg1[i % len(arg1)]) & 0xff

print(encflag)

# wrong = bytearray(wrong)
# decryption(key2, 16, key0, 4, 3)
# decryption(kernel, 13, key2, 16, 143)
# print(kernel)