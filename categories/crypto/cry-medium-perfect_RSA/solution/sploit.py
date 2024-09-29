from pwn import remote
from sage.all import var, gcd
import re
from gmpy2 import mpz
from Crypto.Util.number import isPrime, inverse, long_to_bytes

def gen_perfect_nubers(low_degree: int):
    low_degree //= 2
    high_degree = low_degree + 60
    for i in range(low_degree, high_degree):
        if isPrime(2**i - 1):
            return (2**i - 1) * 2**(i-1)

def get_enc_flag(r: remote):
    r.recvuntil(b"> ")
    r.sendline(b"1")
    enc_flag = int(r.recvline().strip().split(b" = ")[1])
    return enc_flag

def get_sigma(r: remote, x: int):
    r.recvuntil(b"> ")
    r.sendline(b"2")
    r.recvuntil(b": ")
    r.sendline(str(x).encode())
    sigma_x = r.recvline().strip().split(b" = ")[1]
    sigma_x = int(sigma_x)
    return sigma_x

def get_n(r: remote):
    ct_array = []
    e_array = []
    message = 2
    for _ in range(4):
        r.recvuntil(b"> ")
        r.sendline(b"3")
        r.recvuntil(b": ")
        r.sendline(message.to_bytes(1, "big").hex().encode())
        e_array.append(int(r.recvline().strip().split(b" = ")[1]))
        ct_array.append(int(r.recvline().strip().split(b" = ")[1]))
    
    div_array = []
    for i in range(len(ct_array)):
        div_array.append(pow(mpz(message), e_array[i]) - mpz(ct_array[i]))
    N = gcd(div_array)
    return N

def get_flag(p, q, enc_flag):
    e = 65537
    phi = (p-1) * p * (q-1)
    d = int(inverse(e, phi))
    flag = int(pow(enc_flag, d, p**2 * q))
    flag = long_to_bytes(flag)
    return flag

r = remote("85.143.206.150", 13337)

for i in range(9):
    r.recvline()

low_degree = int(re.findall(r"greater than 2\*\*([0-9]+) and less", r.recvuntil(b": ").decode())[0])
perfect_numbers = gen_perfect_nubers(low_degree)
print(perfect_numbers, len(bin(perfect_numbers)[2:]))
r.sendline(str(perfect_numbers).encode())

enc_flag = get_enc_flag(r)

N = get_n(r)
print(f"{N = }, {len(bin(N)[2:]) = }")
Sigma_n = get_sigma(r, N)

x = var('x')
f = x**4  + x**3  +x**2 *(N - Sigma_n + 1) + N*x + N
roots = f.roots()
p = int(roots[-1][0])
assert N % p == 0
q = N // p**2
print(get_flag(p, q, enc_flag))