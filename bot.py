import logging
import json
import traceback

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import settings

logging.basicConfig(format="%(name)s - %(levelname)s - %(message)s",
                    level=logging.INFO,
                    filename="bot.log"
                    )

# reversing dictionary, to make a possibility to check actual auction items
name_to_id_dict = {}
with open("dict_of_items.json", "r", encoding="utf=8") as db_file:
    id_to_name_list = json.load(db_file)
name_to_id_dict = dict([(item[1].lower(), item[0]) for item in id_to_name_list.items()])

realm_lot_dict = {}
with open("auctions-ravencrest.json", "r", encoding="utf=8") as auc_file:
    realm_lot_dict = json.load(auc_file)

# auction commands
def greet_user(bot, update):
    if update is None or update.message is None:
        return
    commands = [
        "/lot *itemname* - minimum price for the item",
        "/itemid *itemname* - shows item ID-number from blizzard database"]
    update.message.reply_text("Hello! I'm Auction bot. The estimated time of auction house update is about 1 hour")
    test_list_of_commands = '\n'.join(commands)
    update.message.reply_text(f"Use one of the commands below:")
    update.message.reply_text(test_list_of_commands)

# Receiving info on preferable item from auction house
def get_lot (bot, update):
    try:
        if update is None or update.message is None:
            return
        lot_name = str(update.message.text.replace('/lot', '')).lower().strip().replace('\n', '').replace('\r', '')
        lot_value = name_to_id_dict.get(lot_name, None)
        price_list = []
        for value in realm_lot_dict['auctions']:
            if lot_value == str(value['item']):
                price_list.append(value['buyout']/value['quantity'])
                stack_size = value['quantity']
                owner_name = value['owner']
                lowest_price_in_stack = min(price_list)/10000
                stack_price = lowest_price_in_stack*value['quantity']


            if lot_value is None:
                raise ValueError("Sorry, this item is not on auction house right now or item name is incorrect")


        update.message.reply_text("Price per item in stack: {}g".format(int(lowest_price_in_stack)))
        update.message.reply_text("Price of item stack: {}g".format(int(stack_price)))
        update.message.reply_text("Stack size: {}".format(stack_size))
        update.message.reply_text("Owner name: {}".format(owner_name))

    except ValueError as e:
        update.message.reply_text(str(e))
        update.message.reply_text('Please enter correct item name')



def item_id(bot, update):
    try:
        if update is None or update.message is None:
            return
        item_name = str(update.message.text.replace('/itemid', '')).lower().strip().replace('\n', '').replace('\r', '')
        value = name_to_id_dict.get(item_name, None)
        update.message.reply_text("This item ID is: {}".format(value))

    except ValueError as e:
        update.message.reply_text(str(e))
        update.message.reply_text('Please enter correct item name')


def main():
    mybot = Updater(settings.API_KEY, request_kwargs=settings.PROXY)

    dp = mybot.dispatcher
    dp.add_handler(CommandHandler("start", greet_user))
    dp.add_handler(CommandHandler("itemid", item_id))
    dp.add_handler(CommandHandler("lot", get_lot))


    mybot.start_polling()
    mybot.idle()


if __name__ == "__main__":
    main()
