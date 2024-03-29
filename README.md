<h1 align="center"> Backend Community Homework: Yatube Project </h1>

[comment]: <> (Logo)
<p align="center">
  <img alt="logo" src="assets/logo.png">
</p>

[comment]: <> (Techs&Badges)
[![Telegram](https://img.shields.io/badge/aaaaaaaalesha-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/aaaaaaaalesha)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
---

## Что это?

Учебный проект блог-платформы для публикации постов и сообществ.

В проекте реализованы следующие возможности, доступные для пользователей:

- [X] парольная аутентификация, восстановление пароля по email;
- [X] публикация новых посты на главной странице и в тематических группах;
- [X] подписки на сообщества избранных авторов;
- [X] комментирование записей;
- [X] добавление изображений к публикуемым постам;
- [X] пагинация постов и кеширование главной страницы;

## Запуск проекта в dev-режиме

- Установите и активируйте виртуальное окружение

```shell
py -3.7 -m venv venv
venv\Scripts\activate
``` 

- Установите зависимости из файла requirements.txt

```shell
pip install -r requirements.txt
``` 

- Для старта, выполните команду:

```shell
python3 yatube\manage.py runserver
```

## Author

Copyright © 2022, [Алексей Александров](https://github.com/aaaaaaaalesha)
