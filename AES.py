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

    # plaintext = 'Привет мир'.encode('utf-8')
    # print(plaintext)
    #
    #
    # print(ciphertext)
    #
    # vector = cipher.iv
    # print(cipher.iv)
    #
    # cipher_2 = AES.new(key, AES.MODE_CBC, vector)
    # plaintext = unpad(cipher_2.decrypt(ciphertext), AES.block_size)
    # print(plaintext.decode())
    with open("C:/Users/artio/Downloads/ChatGPT.png", mode='rb') as picture:
        file = picture.read()
    ciphertext = cipher.encrypt(pad(file, AES.block_size))
    vector = cipher.iv
    deciphertext = AES.new(key, AES.MODE_CBC, vector)
    plaintext = unpad(deciphertext.decrypt(ciphertext), AES.block_size)
    print(file)
    with open("C:/Users/artio/Downloads/cipherChatGPT.png", mode='wb') as cipher_picture:
        cipher_picture.write(ciphertext)
    with open("C:/Users/artio/Downloads/decipherChatGPT.png", mode='wb') as decipher_picture:
        decipher_picture.write(plaintext)