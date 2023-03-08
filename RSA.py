import random
import math
from Primes import getPrime

# def mod_inverse(a, m):
#     for x in range(1, m):
#         if (((a % m) * (x % m)) % m == 1):
#             return x
#     return -1

def inverse(x, modulus):
    if modulus == 0:
        raise ZeroDivisionError("Modulus cannot be zero")
    if modulus < 0:
        raise ValueError("Modulus cannot be negative")
    r_p, r_n = x, modulus
    s_p, s_n = 1, 0
    while r_n > 0:
        q = r_p // r_n
        r_p, r_n = r_n, r_p - q * r_n
        s_p, s_n = s_n, s_p - q * s_n
    if r_p != 1:
        return -1
    while s_p < 0:
        s_p += modulus
    return s_p


def Generate_Keypair():
    p = getPrime(2048)
    q = getPrime(2048)
    n = p * q
    phi = (p - 1)*(q - 1)
    e = random.randrange(1, phi)
    while True:
        # as long as gcd(1,phi(n)) is not 1, keep generating e
        e = random.randrange(1, phi)
        g = math.gcd(e, phi)
        # generate private key
        d = inverse(e, phi)
        if d == -1:
            continue
        elif g == 1 and e != d and d != -1:
            break
    public_key = (e, n)
    private_key = (d, n)
    return public_key, private_key

def encrypt(msg_plaintext, package):
    #unpack key value pair
    e, n = package
    msg_ciphertext = [pow(ord(c), e, n) for c in msg_plaintext]
    return msg_ciphertext

def decrypt(msg_ciphertext, package):
    d, n = package
    msg_plaintext = [chr(pow(c, d, n)) for c in msg_ciphertext]
    # No need to use ord() since c is now a number
    # After decryption, we cast it back to character
    # to be joined in a string for the final result
    return (''.join(msg_plaintext))

if __name__ == "__main__":
    msg = input("Введите сообщение которое хотите зашифровать")
    public, private = Generate_Keypair()
    #with open('encription.txt',mode='w', encoding='UTF-8' ) as file:
    encript_msg = encrypt(msg, public)
    print(encript_msg)
    decrypt_msg = decrypt(encript_msg,private)
    print(decrypt_msg)



