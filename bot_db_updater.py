import requests
import json
import time
import traceback


import os
from bs4 import BeautifulSoup
from wowapi import WowApi

#Загружаем старые данные, если они имеются
try:

    with open("dict_of_items.json", "r", encoding="utf=8") as item_id_in_file:
        item_id_in_file = json.load(item_id_in_file)

except Exception as error:
    print("Произошла ошибка, старые данные не будут загружены")
    print(traceback.format_exc())
    item_id_in_file = {}


# Получаем актуальный список аукционов
try:
    api = WowApi('a2221c916652442bad3fbd0b1581a43d', '3QqAr3a7gJY2Q1PihAUAfwmuRA2SRQFy')
    wow = api.get_auctions('eu', 'ravencrest', locale='en_GB')
    auction = wow['files'][0]['url']
    r = requests.get(auction)
    with open('/aucproject/mybot/auctions-ravencrest.json', 'wb') as f:
        f.write(r.content)

except Exception as error:
    print("Произошла ошибка при загрузке данных из API")
    print(traceback.format_exc())

# дополняем наш словарь новыми ключами, которых там нет
with open("auctions-ravencrest.json", "r", encoding="utf=8") as item_compare_in_file:
    item_compare_in_file = json.load(item_compare_in_file)

try:
    for value in item_compare_in_file['auctions']:
        item_id = str(value['item'])
        if item_id in item_id_in_file:
            pass

        else:
            item_id_in_file[item_id] = None

except Exception as error:
    print("Возникла ошибка, новые значения не были добавлены")
    print(traceback.format_exc())

with open ("dict_of_items.json", "w") as fp:
    json.dump(item_id_in_file, fp)

# для тех ключей у которых нет значений находим имена на сайте
def find_name_by_id(item_id):
    r=requests.get('https://www.wowdb.com/items/{}'.format(item_id))
    #r=requests.get('https://www.wowhead.com/item={}'.format(item_id))
    soup = BeautifulSoup(r.text)
    #return soup.select_one("h1.heading-size-1").text.replace("\n", "")
    return soup.select_one("dt.db-title").text.replace("\n", "")

with open("dict_of_items.json", "r", encoding="utf=8") as id_to_names_file:
    id_to_name_data = json.load(id_to_names_file)
for key, value in id_to_name_data.items():
    try:
        if value is None:
            print('У ключа {} нет значения, поэтому получим его'.format(key))
            value = find_name_by_id(key)
            time.sleep(5)
            id_to_name_data[key]=value
            print(value)
            with open ("dict_of_items.json", "w") as fp:
                json.dump(id_to_name_data, fp)
        else:
            print('У ключа {} есть значение {}'.format(key,value))
    except requests.ConnectionError:
        print('Проблемы с подключением к сети')
    except AttributeError:
        print('Ошибка, что-то пошло не так на странице загрузки')