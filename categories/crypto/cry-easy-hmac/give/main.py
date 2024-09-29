from aiogram import Bot, types # aiogram==2.23.1
from aiogram.dispatcher import Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.files import MemoryStorage
from aiogram import  types
from random import choice
from hashlib import sha256
from pwn import xor
from string import ascii_letters, digits
from secret import menu_final, TOKEN, SECRET_SERVER
import hmac


menu = [
    [InlineKeyboardButton(text="Получить одноразовый ключ 🔑", callback_data="generate_key_1")],
    [InlineKeyboardButton(text="Попробовать открыть сундук🔐", callback_data="open_the_chest")]
]
menu = InlineKeyboardMarkup(inline_keyboard=menu)
ALPHABET = (ascii_letters + digits + "_").encode()
storage = MemoryStorage()
bot = Bot(token = TOKEN)
dp = Dispatcher(bot , storage=storage)


def check_printable(st: bytes) -> bool:
    for i in st:
        a = bytes([i])
        if a not in ALPHABET:
            return False
    return True


def get_random_string(length: int) -> bytes:
    return b"".join([bytes([choice(ALPHABET)]) for _ in range(length)])


class Challenge():
    def __init__(self):
        self.attempt = 5
        self.restart()
    
    def restart(self):
        self.key1 = b""
        self.key2 = b""

    def get_hash_HMAC(self, key: bytes) -> bytes:
        assert check_printable(SECRET_SERVER)
        assert len(SECRET_SERVER) == 32
        hash = hmac.HMAC(xor(SECRET_SERVER, key), SECRET_SERVER, sha256)
        return hash.digest()
    
    def check_hash(self) -> bool:
        self.attempt -= 1
        if self.key1 == self.key2:
            return False
        if self.key1 == "" or self.key2 == "":
            return False
        if not check_printable(self.key1) or not check_printable(self.key2):
            return False
        hash1 = self.get_hash_HMAC(self.key1)
        hash2 = self.get_hash_HMAC(self.key2)
        if hash1 == hash2:
            return True
        else:
            self.restart()
            return False


class FSMForm(StatesGroup):
    key2_ = State()


class Bot_id_challenge():
    def __init__(self):
        self.user_id_chal = {}
    def new_user(self , id):
        self.user_id_chal[id] = Challenge()
    def del_user(self, id):
        self.user_id_chal.pop(id)

bot_id_challenge_ = Bot_id_challenge() 

dict_attempts = {
    4: "4️⃣ попытки",
    3: "3️⃣ попытки",
    2: "2️⃣ попытки",
    1: "1️⃣ попытка",
    0: "0️⃣ попыток"
}

@dp.message_handler(commands=['start'] )
async def start(message: types.Message):
    bot_id_challenge_.new_user(message.from_user.id)
    await message.answer("🏴‍☠️🏴‍☠️🏴‍☠️Йо-хо-хо и бутылка рома!🍾🍾🍾\nЕсли ты здесь, значит ты нашел мой продвинутый сундук!\nЯ современный пират, поэтому и замок на сундуке более замудренный!\nЯ даю тебе 5️⃣ попыток выполнить несложное условие, иначе сундук тебе больше не вскрыть!\nЯ дам тебе свой временный ключ, но он одноразовый!🗝🗝\nИспользуя мой и твой ключ наши хэши должны совпасть🟰🟰🟰, это все, что тебе нужно знать!", reply_markup=menu)
    return

@dp.callback_query_handler(text="generate_key_1")
async def generate_key_1(message: types.Message):
    if not bot_id_challenge_.user_id_chal.get(message.from_user.id):
        return
    if bot_id_challenge_.user_id_chal[message.from_user.id].attempt <= 0:
        await bot.send_message(message.from_user.id, "Сожалею, но больше я тебе своих ключей не дам!")
        await bot.send_message(message.from_user.id, "💀")
    else:
        key1 = get_random_string(32)
        bot_id_challenge_.user_id_chal[message.from_user.id].key1 = key1
        await bot.send_message(message.from_user.id, f"Мой одноразовый ключ🔑: {key1.decode()}")
    await bot.send_message(message.from_user.id,"Меню бота", reply_markup=menu)


@dp.callback_query_handler(text="open_the_chest")
async def open_the_chest(message: types.Message, state: FSMContext):
    if not bot_id_challenge_.user_id_chal.get(message.from_user.id):
        return
    if bot_id_challenge_.user_id_chal.get(message.from_user.id).attempt <= 0:
        await bot.send_message(message.from_user.id, "Сундук для тебя закрыт навсегда! Скажи «прощай» несметному богатству!")
        await bot.send_message(message.from_user.id, "👋")
        await bot.send_message(message.from_user.id, text="Меню бота", reply_markup=menu_final)
        bot_id_challenge_.del_user(message.from_user.id)
        return
    else:
        await bot.send_message(message.from_user.id, "Теперь твой ключ: ")
        await state.set_state(FSMForm.key2_)


@dp.message_handler(state=FSMForm.key2_)
async def get_key_enter(message: types.Message , state: FSMContext):
    user_input = message.text
    await state.reset_state()
    if len(user_input) > 128:
        await bot.send_message(message.from_user.id, "Такой большой ключ не подойдет!💀" )
        await bot.send_message(message.from_user.id,"Меню бота", reply_markup=menu)
        return
    
    bot_id_challenge_.user_id_chal[message.from_user.id].key2 = user_input.encode()
    if bot_id_challenge_.user_id_chal[message.from_user.id].check_hash():
        await bot.send_message(message.from_user.id, "Поздравляю🎉🎉🎉, ты прошел испытание! Ты заслужил награду, лежащую в сундуке!💰💰💰" )
        await bot.send_photo(message.from_user.id, open("flag.jpg", "rb"),  disable_notification=True)
        bot_id_challenge_.del_user(message.from_user.id)
        return
    else:
        attempt = bot_id_challenge_.user_id_chal[message.from_user.id].attempt
        await bot.send_message(message.from_user.id, f"На этот раз ты промахнулся! Попробуй ещё!\nУ тебя осталось: {dict_attempts[attempt]}.")
    await bot.send_message(message.from_user.id,"Меню бота", reply_markup=menu)

if __name__ == '__main__':
    executor.start_polling(dp)