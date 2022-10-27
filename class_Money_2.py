import math
import os.path
from easygui import *

class Money:
    # Ми винесли змінну з __init__, аби зробити її СТАТИЧНОЮ. Ця змінна стосується не об'єктів класу, а САМОГО КЛАСУ. У всіх об'єктах вона спільна, єдина. Комунзім типу
    curs = {"UAH": {"UAH": 1, "DOL": 42, "EUR": 41}, "DOL": {"DOL": 1, "UAH": 0.025, "EUR": 1.02},
                 "EUR": {"EUR": 1, "UAH": 0.024, "DOL": 0.98}}

    def __init__(self, bill, cent, currency):
        self.bill = bill
        self.cent = cent
        self.currency = currency

    def __repr__(self):
        return f"{self.bill}.{self.cent} {self.currency}"

    def minus(self, minus_bill, minus_cent):
        if self.cent >= minus_cent:
            self.cent = self.cent - minus_cent
        else:
            self.bill = self.bill - 1
            self.cent = 100 + self.cent - minus_cent
        self.bill = self.bill - minus_bill

    def converting(self, new_currency):
        new_bill = round(self.bill / Money.curs.get(self.currency).get(new_currency))
        new_cent = round(self.cent / Money.curs.get(self.currency).get(new_currency)) # 575
        if new_cent > 99:
            new_bill = new_bill + math.floor((new_cent/100)) # 5.75
            new_cent = new_cent % 100
            # якщо new_cent = 575, то що робить ця операція: вона ділить на 100 і дивиться, яке число вона максимум може поділити (це 500).
            # Після цього воно дивиться, що лишилось від нашого 500 і повертає його нам
            # КОРОТШЕ: воно повертає нам ту зайву частину, яка не дозволяє йому поділити націло, начисто
        return Money(new_bill, new_cent, new_currency)

    def purchases(self, product):
        converted_money = product.converting(self.currency)
        self.minus(converted_money.bill, converted_money.cent)
        return msgbox(f"Ви купили {product.name}\nВаша здача: {self}\nПриємного дня!",image='b50b4768194455943ca0f1cf07fcf9af.gif')

class Product(Money):
    def __init__(self, bill, cent, currency, name):
        super().__init__(bill, cent, currency)
        self.name = name

    def discount(self, percentage):
        money_num = int(self.bill) + int(self.cent)/100    # 15.50
        percentage = 100 - percentage     # 99 (99% від загальної суми, типу знижка 1%, тому 99%)
        percentage = percentage / 100     # Зараз percentage дорівнюєє 99. Ми мусимо перетворити його в 0.99 (ми множитимемо на 0.99, типу майже на 1, типу трошка менше вийде, так і треба)
        # 15.50 * 0.99
        money_num = money_num * percentage   # 15.50 * 99% ==== 15.50 * 0.99
        #25.50
        #1
        money_num = round(money_num, 2)      # 23.739265917
        return Product(int(str(money_num).split(".")[0]), int(str(money_num).split(".")[1]), self.currency, self.name)


class CashRegister:
    @staticmethod # Якщо ми хочемо викликати функцію БЕЗ ОБ'ЄКТА, а напряму з класу, то дописуємо цю фігнюшку. ЦЕ СТАТИЧНИЙ МЕТОД
    def load_data(path, key):
        data = open(path, 'r', encoding="utf-8")
        data_string = data.read()
        data.close()
        result = {}
        data_cut_above = data_string[data_string.index(key)::]      # Ми взяли наш ключик і стерли всьо зверху. Тепер від ключика до кінця файлу
        data_cut_under = data_cut_above[:data_cut_above.index("\n\n"):].split("\n") # Ми відрізали кусок на місці подвійного нового рядка (пустого рядка). Тепер у нас клапт потрібної нам інфи. ЗРАЗУ Ж перетворимо його в масив по рядочках
        data_cut_under.pop(0)
        final_data = data_cut_under
        for line in final_data:
            elements = line.split("-") # elements = ["Капучино на банановому молоці ","  40.0 UAH "," 1"]
            amount = int(elements[2].strip()) # amount = 1
            if amount > 0:
                result[elements[0].strip() + " - " + elements[1].strip()] = amount # result["Amogus"] = 1
        return result

    @staticmethod
    def load_client(path, client):
        data = open(path, 'r', encoding='utf-8')
        data_string = data.read()
        data.close()
        for line in data_string.split("\n"):
            if line.startswith(client):
                return line
        return "NOT FOUND"

    @staticmethod
    def buying_info_text(product):
        message_string = "Ви хочете придбати: " + product.name + "\nЦіна: " + product.bill + "." + product.cent + " " + product.currency + "\nМаєте карту на знижку?"
        discount_card_choice = buttonbox(message_string, "CoffeeShop", ["Так", "Ні, хочу оформити", "Не цікавить"],image='signing-icon-anim.gif')
        return discount_card_choice

    @staticmethod
    def new_client(path):
        discount_client = enterbox("Вкажіть своє ім'я, або нікнейн для знижки: ", "discount", "")
        file = open(path, 'a', encoding='utf-8')
        file.write(f'{discount_client} 0\n')
        file.close()
        return discount_client

    @staticmethod
    def confirmation(product, product_with_discount, client_persentage):
        message = f"Продукт: {product.name}\nЦіна: {product.bill}.{product.cent} {product.currency}\nЗнижка: {client_persentage}%\nДо оплати: {product_with_discount.bill}.{product_with_discount.cent} {product.currency}\nОберіть вашу валюту:"
        currency = buttonbox(message,"Оберіть валюту", ["UAH", "EUR", "DOL"],image='money.gif')
        wallet_bill = int(enterbox(f'Скільки {currency} ви даєте? (без монет)', "Ціла частина ваших коштів"))
        wallet_cent = int(enterbox(f'Скільки монет ви даєте?', "Копійки ваших коштів"))
        wallet = Money(wallet_bill, wallet_cent, currency)
        msgbox(wallet.purchases(product_with_discount))
        cheklist = os.path.join('data','alreadyBuyed.txt')
        file = open(cheklist, 'a')
        file.write(f'Назва товару: {product.name}. Ціна {product.bill}.{product.cent} {product.currency}\n')
        file.close()

    @staticmethod
    def discount_calculation(discount):
        if discount < 100:
            return 0
        elif discount < 200:
            return 1
        elif discount < 500:
            return 2
        else:
            return 5


inventoryPath = os.path.join('data', 'forSell.txt')
clientsPath = os.path.join('data', 'clients.txt')

while True:
    coffee = CashRegister.load_data(inventoryPath, "Кава:")
    deserts = CashRegister.load_data(inventoryPath, "Cмаколики:")
    menu = {"Кава": coffee, "Смаколики": deserts}
    start_menu = buttonbox("Ласкаво просимо в кав'ярню",'CoffeeShop',['Перейти до покупки', 'Вихід'],image='rosehackstatic.gif')
    if start_menu != 'Перейти до покупки':
        break
    choice = buttonbox("Що бажаєте купити?: ", "CoffeeShop", ["Кава", "Смаколики"],image='99ff0608104912d023a5642ee8baf1b0.gif')
    buttons = list(menu[choice].keys())
    text = " " + str(buttons).replace("[", "").replace("]","").replace("\'", "").replace(",", "\n")
    menu_choice = buttonbox(text, "CoffeeShop", buttons,image='coffee-gif-8.gif')
    # виглядає, наприклад, ось так: Латте - Ціна 40.0 UAH
    product_name = menu_choice.split('-')[0].strip() # все до тере (вийшло Латте)
    product_currency = menu_choice[menu_choice.rindex(" ")::].strip() # Берем частинку після останнього пробілу (вийшло UAH)
    product_price = menu_choice.split('-')[1].strip().split(" ")[1]    # Берем частинку після тере (вийшло Ціна 48.0 UAH). І зразу з ділимо по пробілу і берем другу частинку (вийшло 48.0)
    product_bill = product_price.split('.')[0] # берем наше збережене 48.0 і ділимо по крапочці на основну і дробову частини (bill та cent відповідно)
    product_cent = product_price.split('.')[1]
    chosen_product = Product(product_bill, product_cent, product_currency, product_name)
    discount_card_choice = CashRegister.buying_info_text(chosen_product)
    if discount_card_choice == "Так":
        client_name = enterbox("Ваше ім'я?", "CoffeeShop")
        client = CashRegister.load_client(clientsPath, client_name)
        while client == "NOT FOUND":
            if buttonbox("Вибачте, користувача не знайдено. Спробувати ще раз?", "CoffeeShop", ["Ні", "Так"],image='giphy.gif') == "Ні":
                break
            client_name = enterbox("Ваше ім'я?", "CoffeeShop")
            client = CashRegister.load_client(clientsPath, client_name)
    elif discount_card_choice == "Ні, хочу оформити":
        client_name = CashRegister.new_client(clientsPath)
        client = CashRegister.load_client(clientsPath, client_name)
    else:
        client = "NOT FOUND"
    if client != "NOT FOUND":
        client_persentage = CashRegister.discount_calculation(float(client.split(" ")[1]))
    else:
        client_persentage = 0
    product_with_discount = chosen_product.discount(client_persentage)
    CashRegister.confirmation(chosen_product, product_with_discount, client_persentage)
    if client != "NOT FOUND":
        file = open(clientsPath, 'r', encoding='utf-8')
        clientsString = file.read()
        file.close()
        for line in clientsString.split("\n"):
            if line == client:
                hryvnya_product = product_with_discount.converting("UAH")
                new_sum = float(line.split(" ")[1]) + hryvnya_product.bill + (hryvnya_product.cent/100)
                client_update = line.replace(line.split(" ")[1], str(new_sum))
                clientsString = clientsString.replace(line, client_update)
                file = open(clientsPath, 'w', encoding='utf-8')
                file.write(clientsString)
                file.close()
                break