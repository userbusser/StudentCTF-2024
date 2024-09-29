from Crypto.Util.number import getPrime, bytes_to_long, GCD
from sage.all import sigma, alarm, AlarmInterrupt, cancel_alarm
from random import randint


FLAG = open("FLAG.txt", "rb").read()
START_MESSAGE = '''
|------------------------------------------------|
|                                                |
|         Welcome to the perfect world!          |
| Where everything is perfect, even the numbers! |
|                                                |
|                                                |
|------------------------------------------------|
'''

PERFECT_MESSAGE = "To enter this world, please enter a perfect number that will be greater than 2**{} and less than 2**{}: "

class RSA_and_Sigma_function():
    def __init__(self):
        self.gen_params()
        self.n = self.p ** 2 * self.q
        self.e = 0x10001
        self.phi = (self.q - 1) * self.p * (self.p - 1)

    def gen_params(self):
        self.p = getPrime(512)
        self.q = getPrime(512)

    def encrypt(self, m: bytes, e: int):
        m = bytes_to_long(m)
        if m >= self.n:
            return 0
        Ct = pow(m, e, self.n)
        return Ct
    
    def Sigma_function(self, x: int):
        if x == self.n:
            return sigma(self.p ** 2) * sigma(self.q)
        result = -1
        try:
            alarm(15)
            result = sigma(x)
        except AlarmInterrupt:
            print("Sorry, timmed out!")
        else:
            cancel_alarm()
        return result

class Challenge():
    def __init__(self):
        self.help_RSA_sigma = RSA_and_Sigma_function()

    def get_flag(self):
        return self.help_RSA_sigma.encrypt(FLAG,
                                           self.help_RSA_sigma.e)

    def error_integer(self, message):
        try:
            a = int(input(message))
            return a
        except:
            print("I'm sorry, not integer! Bye!")
            exit()

    def challenge(self):
        print(START_MESSAGE)
        degree = randint(1, 256)

        a = self.error_integer(PERFECT_MESSAGE.format(degree, degree + 60))

        if not (self.help_RSA_sigma.Sigma_function(a) == 2*a and (a >= 2**degree and a <= 2**(degree+60))):
            print("I'm sorry, but this is not a perfect number or number not in the specified interval, access to the perfect world is closed!")
            exit()
        menu = 'Menu:\n1. Get encryption flag.\n2. Get Sigma function from x.\n3. Encrypt RSA with random e.\n0. Exit perfect world.'
        while True:
            print(menu)
            choice = self.error_integer("> ")
            if choice == 1:
                print(f"enc_flag = {self.get_flag()}")
            elif choice == 2:
                x = self.error_integer("Please enter a number x: ")
                print(f"Sigma({x}) = {self.help_RSA_sigma.Sigma_function(x)}")
            elif choice == 3:
                e = randint(2**16, 2**24)
                while GCD(e, self.help_RSA_sigma.phi) != 1:
                    e = randint(2**16, 2**24)
                message = input("Please enter the message you would like to encrypt (in hex format): ")
                try:
                    message = bytes.fromhex(message)
                except:
                    print("Please valid hex format!")
                    continue
                print(f"{e = }")
                print(f"ct = {self.help_RSA_sigma.encrypt(message, e)}")
            elif choice == 0:
                print("Goodbye!")
                exit()
            else:
                print("Invalid choice!")


        
if __name__ == "__main__":
    challenge = Challenge()
    challenge.challenge()