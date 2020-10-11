import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
from PIL import Image, ImageDraw, ImageFont

# VK API import
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
from vk_api import VkUpload 

# OS import
import time
import os
from threading import Thread
import threading

# Help files import
import setings
import intelCasinoQuestions

# VK setings
vk_session = vk_api.VkApi(token = setings.vkDdkgtaApi)
longpoll = VkLongPoll(vk_session)
vk = vk_session.get_api()

print('Создание таблицы ...')
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive'] # что то для чего-то нужно Костыль
creds = ServiceAccountCredentials.from_json_keyfile_name(setings.vkViktorinaJson, scope) # Секретынй файл json для доступа к API
client = gspread.authorize(creds)
sheet = client.open('intelCasino').sheet1 # Имя таблицы

def createCell(countCell):
    sheet.update_cell(1, 1, "id пользователя")
    sheet.update_cell(1, 2, "Имя ")
    sheet.update_cell(1, 3, "Фамилия")
    sheet.update_cell(1, 4, "Название команды")
    indexCell = 4

    for numberQues in range(countCell):
        indexCell += 1
        sheet.update_cell(1, indexCell, f"Вопрос {numberQues+1}") 

questionsData = { # Вопрос : ответ
    "Как называеться ваша команда? " : "komanda",
    """Один известный писатель рассказывал, что списал образ старушки - вредны со своей бывшей жены. 
    При этом бабулька оказалась удивительно похожей на Коко Шанель. На голове у не всегда была 
    шляпка со складной тульей,благодаря которой она и получила прозвище""" : '1',

    """Готовясь к приходу пирата Г. Моргана, монахи столицы Панамы выкрасили 
    священный алтарь в белый цвет. Зачем они это сделали?""" : '2',

    """Сделать это можно в банках или, например, на спортивных соревнованиях. Но, в отличие от банков, 
    на спортивных соревнованиях сделать это можно лишь один раз. Ответьте двумя словами, что именно сделать?""" : '3'
}

createCell(len(questionsData))

print("Таблица создана")

usersId = [] # список людей которые уже учавствуют или уже прошли тест
usersId.append(0) # добавляем фантомного пльзователя 
start = False
rowQuestion = 4
columCell = 0

# class CreateQuestions(threading.Thread):

#     questions = "2"
#     answer = "1"

#     def __init__(self, questions, answer):
#         self.questions = questions
#         self.answer = answer
    
    
    # def printQuestion(self, user_id, random_id, columCell, rowCell):

    #     vk.messages.send( 
    #                     user_id = user_id,
    #                     random_id = random_id,
    #                     message = self.questions,
    #                     )

    #     if getMessege(self.answer, user_id) :
    #         if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
    #             otvet = str(event.text)

    #             sheet.update_cell(columCell, rowCell, "1")
    #             sheet.update_cell(columCell+1 ,rowCell, str(otvet))
    #     else: 
    #         if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id:
    #             otvet = str(event.text)

    #             sheet.update_cell(columCell, rowCell, "0")
    #             sheet.update_cell(columCell+1 ,rowCell, str(otvet))

def printQuestion(random_id, user_id):
    global columCell, questionsData,rowQuestion
    
    columCell += 2
    privateColumCell = columCell
    privateRowCell = rowQuestion

    firstConnection(user_id, privateColumCell)
    
    for questions in questionsData:
        vk.messages.send(
            user_id=user_id,
            random_id=random_id,
            message=questions,
        )

        if getMessege(questionsData[questions], user_id):

            otvet = vk.messages.getHistory(user_id = user_id, count = 1)
            # распарсили ответ
            otvet = otvet['items']
            otvet = otvet[0]
            otvet = otvet['text']

            sheet.update_cell(privateColumCell, privateRowCell, "1")
            sheet.update_cell(privateColumCell+1, privateRowCell, str(otvet))

            privateRowCell += 1
        else:
            
            otvet = vk.messages.getHistory(user_id = user_id, count = 1)
            
            # распарсили ответ
            otvet = otvet['items']
            otvet = otvet[0]
            otvet = otvet['text']

            sheet.update_cell(privateColumCell, privateRowCell, "0")
            sheet.update_cell(privateColumCell+1, privateRowCell, str(otvet))
            privateRowCell += 1
                    
def getMessege (stringOtvet, user_id): # Получаем сообщение от конкретного пользователя
    for event in longpoll.listen(): # цикл для каждго ивента сервера
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.user_id == user_id: # ждать ответа от данного юзера 
            vk.messages.getConversations(offset = 0, count = 1)  
    
            if event.text == stringOtvet: # если событие текст и он равен сообщению которое отправил пользователь
                return True

            return False

def newUser():
    global columCell

    print("Проверка подключения")

    for userId in usersId: # Перебираем список с пользователями 
        if event.user_id == userId:
            print("Старый пользователь...")
            return False 
    print("Новый пользователь...")

    userInfo = vk.users.get(user_ids = event.user_id) 
    print(userInfo)# Получили ответ в виде массива из одного списка
    
    return True

def firstConnection(user_id, columCell):
    # global columCell

    userInfo = vk.users.get(user_ids = user_id)
    userInfo = userInfo[0] 

    sheet.update_cell(columCell, 1, f"""vk.com/id{user_id}""")
    sheet.update_cell(columCell, 2, userInfo["first_name"])
    sheet.update_cell(columCell, 3, userInfo["last_name"])

# def getQuestion(random_id, user_id, questions1):
#     global columCell, rowQuestion

#     firstConnection(user_id)

#     privateColumCell = columCell
#     privateRowCell = rowQuestion

#     for questions in questionsData:
#         doneQuestions = CreateQuestions(questions, questionsData[questions])
       
#         doneQuestions.printQuestion(user_id,random_id, privateColumCell, privateRowCell)
#         privateRowCell += 1 
        # print(": ",event.text)
        # input("ждем других \n")
        
for event in longpoll.listen():
    print(event.type)

    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        vk.messages.getConversations(offset = 0, count = 1)  
        if event.text == "А" or 'а':
            start = True
        # start = getMessege("2020", event.user_id)
        if start:
            whoUser = newUser()
            # whoUser = True
        
            if whoUser:
                print("Новый пользователь")
                usersId.append(event.user_id)

                Thread(target=printQuestion, args=(event.random_id, event.user_id,)).start() # Запуск нового потока для нового пользвоателя
            else:
                print("Старый пользователь")

