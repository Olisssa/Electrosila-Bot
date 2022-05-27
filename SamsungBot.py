import telebot
from telebot import types
import requests
from bs4 import BeautifulSoup


bot = telebot.TeleBot("")


@bot.message_handler(commands=["start"])
# a message handler which handles incoming /start command
def start(message):
    """
    a function for welcome message, asking the user and offering him the answer options
    it has one parameter (the message)
    """
    chat_id = message.chat.id
    first_name = message.chat.first_name
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard0 = types.KeyboardButton(text="да")
    keyboard1 = types.KeyboardButton(text="нет")
    markup.add(keyboard0, keyboard1)
    bot.send_message(chat_id, f"Здравствуйте, {first_name}!\n"
                     "Интересуетесь ассортиментом смартфонов SAMSUNG в магазине Электросила?", reply_markup=markup)


@bot.message_handler(content_types=["text"])
# a message handler which handles user's answer
def text(message):
    """
    a function for parsing of names, images, prices and links of smartphones
    it has one parameter (the message)
    """
    chat_id = message.chat.id
    if message.chat.type == "private":
        if message.text == "да":
            base_url = "https://sila.by/catalog/mobilnye_telefony/SAMSUNG/page/"
            response = requests.get(base_url).text
            soup = BeautifulSoup(response.encode('ISO-8859-1'), "html.parser")
            urls = [base_url, ]
            # it's a list of the urls, if there is only 1 page
            try:
                # try to create the list of urls (if there are more than 1 page)
                total_pages = int(soup.find("div", class_="pages").findAll("a")[-2].text)
                # count the number of pages
                urls = [base_url + str(x) for x in range(1, total_pages + 1)]
                # create the list of pages' urls
            except AttributeError:
                print("there is only 1 page")
            finally:
                for url in urls:
                    # search all sections with required items
                    response = requests.get(url).text
                    soup = BeautifulSoup(response.encode('ISO-8859-1'), "html.parser")
                    section = soup.find_all("div", class_="tovars")
                    for products in section:
                        # search all required items in all sections
                        product = products.find_all("div", class_="tov_prew")
                        for item in product:
                            # search names, images, prices and links of items in all sections
                            product_name = item.find("strong").get_text(strip=True)
                            product_image = item.find("a").find("img").get("src")
                            product_price = item.find("div", class_="price").get_text(strip=True)
                            product_link = item.find("a").get("href")
                            all_products = f"{product_name}\n" \
                                           f"{product_image}\n" \
                                           f"Ссылка : {product_link}\n" \
                                           f"Цена (со скидкой, без скидки) : {product_price}"
                            # declare a variable and put received data on it
                            bot.send_message(chat_id, all_products)
                bot.send_message(chat_id, "Всё:)")

        elif message.text == "нет":
            bot.send_message(chat_id, f"До свидания:(")


bot.polling(none_stop=True)