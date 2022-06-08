# RUS
# ScratchPlus
## Что такое ScratchPlus?
**ScratchPlus** - это библиотека для работы со Scratch Api для Python :snake:.
## Что может наш модуль?
- [✔️] Работать с данными скретча
- [✔️] Писать и читать комментарии 
- [✔️] Работать с облачными проектами на Scratch
- [❌] Регестрироватся на Scratch
- [✔️] Читать форумы и получать данные о постах
- [✔️] Кодирование числовых облачных данных скретча в обычные строки
- [❌] Постить на форумах
## Преимущества перед аналогом (ScratchClient)
- [👍] Возможность автоматический кодировать и декодировать облачные данные  
- [👍] Чтение комментариев профиля путём парсинга
- [👍] Если вы не хотите входить в аккаунт, есть Read-Only режим.
- [👍] Вы можете войти в несколько аккаунтов сразу и выполнять от них действия в асинхронном режиме

## Используймые библеотеки  или API:
- [Requests](github.com/psf/requests) - Библеотека Для удобной работы с протоколом HTTP.
- [ScratchDB](https://scratchdb.lefty.one/) - API Для работы с форумами на Scratch.
- [IsScratcher](https://github.com/hello-smile6/isScratcher) - API Для проверки статуса Скретчера

## Установка
Для установки можно возпользоваться командой
```pip install scratchplus```
## Начало
Первым Quick Start у нас будет скрипт, для оставления комментариев на профиле пользователя
```python
from scratchplus import Session # импротируем сессию
ses = Session("username_on_scratch", "password") # входим в аккаунт
user = ses.get_user("gagarintentoper") # получаем пользователя
user.post_comment("Привет Scratch+ разработчик!") # оставляем комментарий
```
## Документация
### Подключение к аккаунту
Для работы с большей части API нужно авторизоваться (см. ниже)
```python
from scratchplus import Session
account = Session("username_on_scratch", "password")
```
### Методы Get
После авторизации, мы можем получить объект из APi для далнейшей работы с ним
Здесь будет приведёт список всех Get Заросов 
#### get_user
```python
account.get_user("username")
```
Метод возращает объект класса YourUser или AnotherUser 
#### get_project
```python
account.get_project(22814354) # ID проекта как аргумент
```
Метод возращает объект класса YourProject или AnotherProject 

#### USER
Здесь будет документация по классу User
```python
print(user.id) # Выведет user id
print(user.username) # Выведет username
print(user.joined_timestamp) # Выведет user дата присоединения к скретчу 
print(user.scratchteam) # Выведет, относиться ли пользователь к ScratchTeam (True / False)
print(user.get_projects(all=False, limit=20, offset=0)) # Выведет список проектов, созданных user. Флаг all нужен, если вы хотите получить все проекты. 
print(user.get_curating(all=False, limit=20, offset=0)) # Выведет список студий, которые курирует user. Флаг all нужен, если вы хотите получить все студии. 
print(user.get_favorites(all=False, limit=20, offset=0)) # Выведет список избранных проектов. Флаг all нужен, если вы хотите получить все избранные проекты. 
print(user.get_followers(all=False, limit=20, offset=0)) # Выведет список подписчиков пользователя user. Флаг all нужен, если вы хотите получить всех подписчиков.
print(user.get_following(all=False, limit=20, offset=0)) # Выведет список пользователей, на которых подписался user. Флаг all нужен, если вы хотите получить все подписки к пользователям. 
print(user.get_message_count()) # Выведет количество сообщений в скретче у user
print(user.get_comments(page=1)) # Выведет все комментарии со страницы на профиле user
user.post_comment(content, parent_id="", commentee_id="") # Оставит комментарий на профиле user. В параметр parent_id id комментария, под которым вы хотите оставить новый. 
user.toggle_commenting() # Включает/Выключает комментирование на профиле user, работает только на профиле аккаунта, в который вы вошли
user.follow() # Подписываеться на user
user.unfollow() # Отписываеться от гser
user.report(field) # Посылает репорт на user. Field - поле выбора причины репорта (Username/Icon/About Me/What I'm Working On) 
```
## Спасибо
- Пользователю github Quatum-Codes за парсер комментариев

# ENG
# Scratch Plus
## What is ScratchPlus?
**ScratchPlus** is a Scratch API library for Python :snake:.
## What can our module do?
- [✔️] Work with scratch data
- [✔️] Write and read comments
- [✔️] Work with cloud projects on Scratch
- [❌] Register on Scratch
- [✔️] Read forums and get post data
- [✔️] Encode scratch numeric cloud data into normal strings
- [❌] Post on forums
## Advantages over analogue (ScratchClient)
- [👍] Ability to automatically encode and decode cloud data
- [👍] Read profile comments by parsing
- [👍] If you don't want to login, there is a Read-Only mode.
- [👍] You can log in to multiple accounts at once and perform actions from them asynchronously

## Libraries or APIs used:
- [Requests](github.com/psf/requests) - Library For convenient work with the HTTP protocol.
- [ScratchDB](https://scratchdb.lefty.one/) - API For working with Scratch forums.
- [IsScratcher](https://github.com/hello-smile6/isScratcher) - API To check Scratcher status

## Installation
To install, you can use the command
```pip install scratchplus```
## Quick Start
```python
from scratchplus import Session # import Session
ses = Session("username_on_scratch", "password") # log in
user = ses.get_user("gagarintentoper") # get user
user.post_comment("Hello Scratch+ devloper!") # post the comment
```
## Documentation
### Account connection
To work with most of the API, you need to log in (see below)
```python
from scratchplus import Session
account = Session("username_on_scratch", "password")
```
### Get Methods
After authorization, we can get an object from API for further work with it
This will list all Get Zaros
#### get_user
```python
account.get_user("username")
```
The method returns an object of class YourUser or AnotherUser
#### get_project
```python
account.get_project(22814354) # project ID as argument
```
The method returns an object of class YourProject or AnotherProject

#### USER
There will be documentation on the User class
```python
print(user.id) # Print user id
print(user.username) # Print username
print(user.joined_timestamp) # Prints the date the user joined the scratch
print(user.scratchteam) # Print if user belongs to ScratchTeam (True / False)
print(user.get_projects(all=False, limit=20, offset=0)) # Lists projects created by user. The all flag is needed if you want to get all projects.
print(user.get_curating(all=False, limit=20, offset=0)) # Lists the studios the user is curating. The all flag is needed if you want to get all the studios.
print(user.get_favorites(all=False, limit=20, offset=0)) # List favorite projects. The all flag is needed if you want to get all featured projects.
print(user.get_followers(all=False, limit=20, offset=0)) # Lists followers of user user. The all flag is needed if you want to get all subscribers.
print(user.get_following(all=False, limit=20, offset=0)) # Print a list of users that user has followed. The all flag is needed if you want to get all user subscriptions.
print(user.get_message_count()) # Prints the number of messages in the user's scratch
print(user.get_comments(page=1)) # Print all comments from a page on the user's profile
user.post_comment(content, parent_id="", commentee_id="") # Post a comment on user's profile. In the parent_id parameter, the id of the comment under which you want to leave a new one.
user.toggle_commenting() # Turns on/off commenting on the user profile, only works on the profile of the account you are logged into
user.follow() # Follow user
user.unfollow() # Unfollow ser
user.report(field) # Sends a report to user. Field - field for selecting the reason for the report (Username/Icon/About Me/What I'm Working On)
```

## Thanks
- To github user Quatum-Codes for the comment parser
