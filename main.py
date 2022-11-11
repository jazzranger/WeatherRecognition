import psycopg2
import requests
import telebot
import urllib.request
import os

import img_tools


class Database:
    def __init__(self):
        self.con = self.connect_server()
        self.cur = self.con.cursor()


    def get_user(self, userId):
        self.cur.execute('''SELECT COUNT(*) FROM "User" WHERE ("Extid") = ('{0}')'''.format(userId))
        user = self.cur.fetchall()
        return int(user[0][0])

    def get_classes(self):
        self.cur.execute('''SELECT * FROM "Class"''')
        classes = self.cur.fetchall()
        return classes

    def get_pictures(self):
        self.cur.execute('''SELECT "nameImg" FROM "Image" ORDER BY RANDOM() LIMIT 4''')
        namesImg = self.cur.fetchall()
        return namesImg

    def get_pictures_null_class(self):
        self.cur.execute('''SELECT "nameImg" FROM "Image" WHERE ("classId") IS NULL ORDER BY RANDOM() LIMIT 1''')
        namesImg = self.cur.fetchall()
        return namesImg


    def get_answerUser(self, userId):
        self.cur.execute('''SELECT * FROM "User" WHERE ("Extid") = ('{0}')'''.format(userId))
        user = self.cur.fetchall()
        return int(user[0][0])

    def get_answerPic(self, namePic):
        self.cur.execute('''SELECT * FROM "Image" WHERE ("nameImg") = ('{0}')'''.format(namePic))
        name = self.cur.fetchall()
        return name[0][0]

    def add_answer(self, classId, userId, imageName):
        answerPic = self.get_answerPic(imageName)
        answerUser = self.get_answerUser(userId)
        self.cur.execute('''INSERT INTO "Estimation" ("Class","User","Image") VALUES('{0}','{1}',{2})'''.format(classId, answerUser, answerPic))
        self.con.commit()


    def add_user(self, userId):
        self.cur.execute('''INSERT INTO "User" ("Extid") VALUES('{0}')'''.format(userId))
        self.con.commit()

    def current_user(self, userId):
        count = 0
        user = {
            "userId": userId,
            "pic_index": count
        }
        return user


    def connect_server(self):
        return psycopg2.connect( host="ec2-63-32-248-14.eu-west-1.compute.amazonaws.com", database="dlm6krnhu1c4l", user="bkrgiivouzonyq", password="7928919c2d50f945aa81dbeee68b3b917e49b761637bbb55112096e48545eafb")





def start_bot():
    db = Database()
    bot = telebot.TeleBot("5600244388:AAHyy6G5IG-7hVD6XQ4zuQByJ8xS21OyItQ")
    chatIDs = []
    images = []
    users = []

    #imagesName = [i[0] for i in db.get_pictures()] # переделать т.к фотки повторяются

    def getIndex(chatId):
        reversed_list_index = chatIDs[::-1].index(chatId)
        original_list_index = len(chatIDs) - 1 - reversed_list_index
        return original_list_index

    @bot.message_handler(commands=['start'])
    def getMessage(message):
        #bot.send_message(message.from_user.id, "Hello")
        if db.get_user(message.chat.id) == 0:
            db.add_user(message.chat.id)
        user = db.current_user(message.chat.id)
        chatIDs.append(user['userId'])
        users.append(user)
        image = [i[0] for i in db.get_pictures()]
        print(db.get_pictures_null_class()[0][0])
        image.append(db.get_pictures_null_class()[0][0])
        print(image)
        images.append(image)


        index = getIndex(message.chat.id)

        curr_image = images[index][users[index]['pic_index']]
        print(curr_image)
        curr_count = users[index]['pic_index']
        print(curr_count)

        post = getPicture(user, index)
        if post is not None:
            #p = open("dataset/{0}".format(curr_image), "rb")
            #print(img_tools.download_img(curr_image).decode("utf-8") )
            p = img_tools.download_img(curr_image)
            print(type(p))
            bot.send_photo(message.chat.id, p)
            bot.send_message(message.from_user.id, post["text"], reply_markup=post["keybord"])

    def getPicture(user, index):

        if user["pic_index"] == len(images[index]):

            text = "Спасибо за участие в разметке ❤️ ฅ(•ㅅ•❀)ฅ"
            return {
                "text": text,
                "keybord": None
            }
        else:
            answers = db.get_classes()
            keybord = telebot.types.InlineKeyboardMarkup()
            for answer_index, answer in answers:
                keybord.row(telebot.types.InlineKeyboardButton(f"{answer}", callback_data=f"{answer_index}"))
            text = "Выберите наиболее подходящий класс:"
            return {
                "text": text,
                "keybord": keybord
            }


    @bot.callback_query_handler(func = lambda query:query.data)
    def answer(query):
        index = getIndex(query.message.chat.id)
        user = users[index]
        print(query.data)
        db.add_answer(query.data, query.message.chat.id, images[index][users[index]['pic_index']])
        user["pic_index"] += 1

        post = getPicture(user, index)
        if post is not None:
            if user["pic_index"] != len(images[index]):
                curr_image = images[index][users[index]['pic_index']]
                #p = open("dataset/{0}".format(curr_image), "rb")
                p = img_tools.download_img(curr_image)
                print(type(p))
                bot.send_photo(query.message.chat.id, p)
                bot.send_message(query.message.chat.id, post["text"], reply_markup=post["keybord"])

            elif user["pic_index"] == len(images[index]):
                user["pic_index"] = 0
                bot.send_message(query.message.chat.id, post["text"], reply_markup=post["keybord"])

    bot.polling(none_stop=False, interval=0)

if __name__ == '__main__':
    #check()
    start_bot()



