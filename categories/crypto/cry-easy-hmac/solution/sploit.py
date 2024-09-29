from pyrogram import Client
import time
from string import ascii_letters, digits

ALPHABET = ascii_letters + digits + "_"

app = Client("my_account")
async def main():
    async with app:
        i = 0
        while i < len(ALPHABET):
            res = await app.send_message("@pirate_chest_bot", "/start")
            time.sleep(1)
            id = res.id
            end = False
            for _ in range(5):
                try:
                    await app.request_callback_answer("pirate_chest_bot", id+1, callback_data="generate_key_1", timeout=1)
                except:
                    pass
                time.sleep(3)
                res = await app.get_messages("pirate_chest_bot", message_ids=id+2)
                key1 = res.text.split(": ")[1]
                key2 = key1 + ALPHABET[i]
                print(key2)
                i+= 1
                try:
                    await app.request_callback_answer("pirate_chest_bot", id+3, callback_data="open_the_chest", timeout=1)
                except:
                    pass
                time.sleep(2)
                res = await app.send_message("pirate_chest_bot", key2)
                id = res.id
                time.sleep(3)
                res = await app.get_messages("pirate_chest_bot", message_ids=id+1)
                if "На этот раз ты промахнулся!" in res.text:
                    id = res.id
                    continue
                else:
                    end = True
                    break
            if end:
                break

app.run(main())