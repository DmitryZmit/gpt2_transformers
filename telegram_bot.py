import telebot

from telebot import types

import pickle as pkl
import sys
import os
import codecs
import re
from gpt2_training.train_utils import load_model, boolean_string, set_lr, get_eval_list_same_length

import argparse
from gen_answer import Gen_answer

parser = argparse.ArgumentParser()
parser.add_argument('--model_name_or_path', type=str,
                    help='pretrained model name or path to local checkpoint')
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--max_seq_length", type=int, default=128)
parser.add_argument("--context_length", type=int, default=4)
parser.add_argument("--init_checkpoint", type=str)
parser.add_argument('--telegram_token', type=str,
                    help='telegram bot token')
parser.add_argument("--fp16", type=boolean_string, default=False)
parser.add_argument("--no_token_id", type=boolean_string, default=True)



# do normal parsing
args = parser.parse_args()
tel_id=str(args.telegram_token).replace(':','_')
log_file='./log_file'+tel_id+'.log'
log_fail_file='./log_fail_file'+tel_id+'.log'
bot = telebot.TeleBot(args.telegram_token)
model=Gen_answer(args=args)

text_message=''

def replace_end_of_sentence(dig_text):
    dig_list=re.findall(r'([?!.]\s*$)',dig_text)
    if len(dig_list)==0:
        dig_text=dig_text+'.'
    return dig_text

act_rep={}
last_intent=''
win=args.context_length

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
    global text_message
    global act_rep
    global win
    if message.chat.id not in act_rep:
        act_rep[message.chat.id] = []
    text = replace_end_of_sentence(message.text)
    act_rep[message.chat.id].append(text)
    if len(act_rep[message.chat.id])>win:
        act_rep[message.chat.id]=act_rep[message.chat.id][1:]
    context=' '.join(act_rep[message.chat.id])
    answer= model.get_answer(act_rep[message.chat.id])
    answer=answer.replace('и<UNK>','й')
    act_rep[message.chat.id].append(answer)
    if len(act_rep[message.chat.id])>win:
        act_rep[message.chat.id]=act_rep[message.chat.id][1:]
    keyboard = types.InlineKeyboardMarkup()
    dislike_button = types.InlineKeyboardButton(text="Неуместно", callback_data='dislike')
    keyboard.add(dislike_button)


    like_button = types.InlineKeyboardButton(text="Круто", callback_data='like')
    keyboard.add(like_button)
    with codecs.open(log_file, 'a', encoding='utf-8') as f:
        f.write(str(message.from_user.id) + ";" + str(message.chat.id) + ";" + str(message.message_id) + ";" + ' '.join(act_rep[
            message.chat.id]) + ";"
                + message.text + ";" + answer + "\n")
    bot.send_message(message.chat.id,text=answer,reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):

    if call.data == 'dislike':
        bot.answer_callback_query(call.id, "Принято")
        with codecs.open(log_fail_file, 'a',encoding='utf-8') as f:
            f.write(str(call.from_user.id) + ";" +str(call.message.chat.id) + ";"+ str(call.message.message_id) +";dislike"+ "\n")
    if call.data == 'like':
        bot.answer_callback_query(call.id, "Принято")
        with codecs.open(log_fail_file, 'a',encoding='utf-8') as f:
            f.write(str(call.from_user.id) + ";" +str(call.message.chat.id) + ";"+ str(call.message.message_id)+";like"+ "\n")





# Обработчик для документов и аудиофайлов
@bot.message_handler(content_types=['document', 'audio'])
def handle_document_audio(message):
    pass

if __name__ == '__main__':

    try:
        bot.polling(none_stop=True, interval=0,timeout=1000)
    except :
        print('Error')
