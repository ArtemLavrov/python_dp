import os, aes_shifr
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
if __name__ == "__main__":
    key = get_random_bytes(16)
    print(key)
    cipher = AES.new(key, AES.MODE_CBC)
    plaintext = 'Привет мир'.encode('utf-8')
    print(plaintext)

    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))
    print(ciphertext)

    vector = cipher.iv
    print(cipher.iv)

    cipher_2 = AES.new(key, AES.MODE_CBC, vector)
    plaintext = unpad(cipher_2.decrypt(ciphertext), AES.block_size)
    print(plaintext.decode())

