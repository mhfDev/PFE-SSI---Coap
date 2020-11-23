
from pybase64 import b64encode,b64decode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad



data ="{\"uid\":\"59 37 BC B9\" , \"status\":\"1\"}"
d=eval(data)
print(d["uid"])
print(d["status"])
key = 'abcdefghijklmnop'
cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
ct_bytes = cipher.encrypt(pad(data, AES.block_size))
# iv = b64encode(cipher.iv).decode('utf-8')
ct = b64encode(ct_bytes).decode('utf-8')
print(ct)

# ivd = b64decode(iv)
# ct='7mU4dBBIJOP4MPdUgx5hJw=='
ctd = b64decode(ct)

cipher = AES.new(key, AES.MODE_CBC,iv=b'0000000000000000')
pt = unpad(cipher.decrypt(ctd), AES.block_size)
print("The message was: ", pt)