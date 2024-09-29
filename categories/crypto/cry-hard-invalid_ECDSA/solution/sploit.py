from sage.all import *
from requests import Session, get
from struct import pack, unpack
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse
import json
import base64
from hashlib import sha256
import re

URL = "http://85.143.206.150:13339"
p = 0xffffffff00000001000000000000000000000000ffffffffffffffffffffffff
a = 0xffffffff00000001000000000000000000000000fffffffffffffffffffffffc
b = 0x5ac635d8aa3a93e7b3ebbd55769886bc651d06b0cc53b0f63bce3c3e27d2604b
N_secp_256 = 0xffffffff00000000ffffffffffffffffbce6faada7179e84f3b9cac2fc632551
Gx, Gy = 0x6b17d1f2e12c4247f8bce6e563a440f277037d812deb33a0f4a13945d898c296, 0x4fe342e2fe1a7f9b8ee7eb4a7c0f9e162bce33576b315ececbb6406837bf51f5

def gen_new_Elliptic_curve():
    for i in range(12, 13):
        try:
            E = EllipticCurve(GF(p), [a, i])
        except:
            continue
        q = E.order()
        divisors_q = divisors(q)
        for divisor_i in divisors_q:
            if len(bin(divisor_i)[2:]) == 72:
                l = q // divisor_i
                break
        j = 2
        while True:
                G = E.lift_x(GF(p)(j))
                if G.order() == q:
                    G_new = l * G 
                    return E, G_new, G_new.order()
                j += 1

         
def get_secret_key(E, data, signature, G, new_n):
    h = sha256(data).digest()
    h = bytes_to_long(h)

    lenght_r = unpack(">I", signature[:4])[0]
    r = bytes_to_long(signature[4:4+lenght_r])
    s = bytes_to_long(signature[8+lenght_r:]) 

    Q = E.lift_x(GF(p)(r))
    Q1 = E(Q.xy()[0], -Q.xy()[1])
    k = discrete_log(Q, G, new_n, operation="+")
    k1 = discrete_log(Q1, G, new_n, operation="+")
    secret_key = (s* k - h) * inverse(r, N_secp_256) % N_secp_256
    secret_key_1 = (s* k1 - h) * inverse(r, N_secp_256) % N_secp_256
    return [int(secret_key), int(secret_key_1)]


def get_new_signature(data, private_key):
    h = sha256(data).digest()
    h = bytes_to_long(h)

    E = EllipticCurve(GF(p), [a, b])
    G = E((Gx, Gy))
    r = 0
    while r == 0:
        k = 2
        r = int((G * k).xy()[0])
    s = int(inverse(k, N_secp_256) * (h + private_key * r) % N_secp_256)
    signature = (long_to_bytes(r), long_to_bytes(s))
    signature = b"".join([pack(">I", len(x)) + x for x in signature])
    return signature


def get_flag(type_data, data, secret_key):
    new_signature = get_new_signature(json.dumps(data).encode(), secret_key)
    new_cookie = b".".join([base64.b64encode(json.dumps(type_data).encode()), 
                            base64.b64encode(json.dumps(data).encode()), 
                            base64.b64encode(new_signature)])
    response_ = get(f"{URL}/vip", cookies={'session': new_cookie.decode()})
    if "stctf{" in response_.text:
        flag = re.findall(r"stctf{(.*)}", response_.text)[0]
    else:
        flag = None
    return flag


Elliptic_curve, G_new, new_n = gen_new_Elliptic_curve()
print(f"{G_new=}")
s = Session()
r = s.post(f"{URL}/sign", 
            data={'username':'a', 'password': 'a'})
s.post(f"{URL}/ecdsa_sign", 
        data={'curve_name':"custom", 
                "gx": G_new.xy()[0], 
                "gy": G_new.xy()[1]})
cookie = s.cookies.get("session")

array_cookie = cookie.split(".")
array_cookie = [json.loads(base64.b64decode(i)) for i in array_cookie[:2]] + [base64.b64decode(array_cookie[2])]
type_data, data, signature = array_cookie

array_secret_key = get_secret_key(Elliptic_curve, json.dumps(data).encode(), signature, G_new, new_n)
print(f"{array_secret_key = }")
data["is_vip"] = True
for secret_key in array_secret_key:
    flag = get_flag(type_data, data, secret_key)
    if flag:
        print("stctf{" + flag + "}")

