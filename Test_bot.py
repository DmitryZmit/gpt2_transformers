import telebot


bot = telebot.TeleBot('844604873:AAEAKFrhk_Ex3cv3AeX1OjtrJFUKUjBCLNw')


# Обработчи к команд
@bot.message_handler(commands=['len_context'])
def handle_intent_list(message):
    global win
    st = f'Длинна контекста: {win}'
    bot.send_message(message.chat.id, st)


@bot.message_handler(commands=['start'])
def handle_intent_list(message):
    st='Привет! Давай поболтаем о чем-нибудь!) Я пока не совсем умная и иногда я могу ответить не в тему. Для удаления контекста введите /del_context'
    bot.send_message(message.chat.id, st)
    global act_rep
    act_rep[message.chat.id]=[]

@bot.message_handler(commands=['del_context'])
def handle_intent_list(message):
    st='Контекст удален'
    bot.send_message(message.chat.id, st)
    global act_rep
    act_rep[message.chat.id]=[]

@bot.message_handler(commands=['context'])
def handle_intent_list(message):
    global act_rep
    bot.send_message(message.chat.id, "Context: "+' '.join(act_rep[message.chat.id]))


@bot.message_handler(content_types=["text"])
def handle_text(message):
    print(message.text)






if __name__ == '__main__':

    try:

        bot.polling(none_stop=True, interval=0,timeout=1000)

    except :
        print('Error')
