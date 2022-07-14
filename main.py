import config
from cats_operations import get_description_and_save_cat, get_cat
from threading import Thread
from telebot import TeleBot
from time import sleep
from typing import BinaryIO
from os import environ
import schedule


bot: TeleBot = TeleBot(environ["TG_BOT_TOKEN"])


def get_description_wrapper(message, image: bytes) -> None:
    # get_description_and_save_cat function wrapper.

    code: int = get_description_and_save_cat(message, image)
    if code == 1:
        bot.reply_to(message, "Опис має заборонені символи.\nНадішліть валідний опис.")
        bot.register_next_step_handler(message, lambda m: get_description_wrapper(m, image))
        return
    elif code == 2:
        for admin in config.ADMIN:
            bot.send_message(admin, "Error while uploading ftp file!")
        return


def send_cat() -> None:
    # Send a cat to TG channel (with get_cat function).

    imgdescr: tuple = get_cat()
    image: bytes = imgdescr[0]
    description: str = imgdescr[1]
    bot.send_photo(config.CHAT_ID, image, description)


@bot.message_handler(content_types=["photo"])
def photo(message):
    # Photo-messages from admins handler.

    if message.chat.id in config.ADMIN:
        bot.reply_to(message, "Надішліть опис зображення.")
        image: bytes = bot.download_file(bot.get_file(message.photo[-1].file_id).file_path)
        bot.register_next_step_handler(message, lambda m: get_description_wrapper(m, image))


def scheduler() -> None:
    # Scheduler function.
    
    while True:
        schedule.run_pending()
        sleep(60)


def main() -> int:
    # Main function. Returns exit code.

    try:
        for time in config.TIME_FOR_CAT:  # Schedule cats sending.
            schedule.every().day.at(time).do(send_cat)

        schedule_thread = Thread(target=scheduler)
        schedule_thread.start()

        bot.infinity_polling()
    except Exception as e:
        print(e)
        return 1

    return 0


if __name__ == "__main__":
    exit(main())