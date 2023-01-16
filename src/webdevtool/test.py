import os

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import algorithms, Cipher, modes

aes_key = os.urandom(32)
aes_iv = os.urandom(16)
print('aes_key: ', aes_key)
print('aes_iv: ', aes_iv)
cipher = Cipher(
    algorithms.AES(aes_key),
    modes.CBC(aes_iv)
)
enc = cipher.encryptor()

padder = padding.PKCS7(algorithms.AES.block_size).padder()

padded_data = padder.update('12334'.encode('utf8')) + padder.finalize()

padded_data = enc.update(padded_data)

print(padded_data)

dec = cipher.decryptor()

unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()

data = unpadder.update(dec.update(padded_data))

try:
    uppadded_data = data + unpadder.finalize()
except ValueError:
    raise Exception('无效的加密信息!')

print(uppadded_data)