import os, aes_shifr
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
if __name__ == "__main__":
    data = b'fvnsjdnvcjsdncmskd;csjmdkcnmskjdncsdc'

    key = get_random_bytes(16)


    # key = os.urandom(16)
    # iv = os.urandom(16)
    # with open('D:/encrypt.txt', mode='r') as file:
    #     current_file=file.readline()
    # encrypted = aes_shifr.AES.encrypt(b'%s' % current_file, key)
    # print(encrypted)
    # encrypted = aes_shifr.AES(key).encrypt(current_file)
    #
    # print(encrypted)
    # decrypted = aes_shifr.AES(key).decrypt(encrypted)
    # print(decrypted)