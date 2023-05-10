import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
if __name__ == "__main__":
    # def genAESmetriks():
    #     key = get_random_bytes(16)
    #     cipher = AES.new(key, AES.MODE_CBC)
    #     vector = cipher.iv
    #     return key, vector,cipher
    # def cipher(file, key, vector, cipher):
    #     ciphertext = cipher.encrypt(pad(file, AES.block_size))
    #     return ciphertext
    #
    # def decipher(d_file, d_key, d_vector):
    #     decipher = AES.new(d_key, AES.MODE_CBC, d_vector)
    #     decipherfile = unpad(decipher.decrypt(d_file, AES.block_size))
    #     return decipherfile
    #
    # plaintext = 'Привет мир'.encode('utf-8')
    # print(plaintext)
    #
    #
    # print(ciphertext)
    #
    # vector = cipher.iv
    # print(cipher.iv)
    str = "Привет мир"
    msg = bytes(str, encoding='utf-8')
    hash_msg=hashlib.sha256(msg).hexdigest()
    key = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC)
    vector = cipher.iv
    ciphertext = cipher.encrypt(pad(msg, AES.block_size))
    cipher_2 = AES.new(key, AES.MODE_CBC, vector)
    plaintext = unpad(cipher_2.decrypt(ciphertext), AES.block_size)
    hash_decipher_msg = hashlib.sha256(plaintext).hexdigest()
    print(plaintext.decode('utf-8'))
