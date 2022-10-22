<h1 align="left">Проект Foodgram</h1>

![example workflow](https://github.com/Alex-code-sxg/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## Общее описание:

Он-лайн сервис "Продуктовый помошник" предоставляет пользователям возможность:

адрес http://130.193.54.149/

* публиковать рецепты, 
* подписываться на публикации других пользователей,
* добавлять понравившиеся рецепты в список «Избранное», 
* перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Инструкция по запуску проекта:

1. Склонировать репозиторий с проектом на свой компьютер.

```
git clone git@github.com:Alex-code-sxg/foodgram-project-react.git
```

2. Запустить сборку образов и контейнеров из директории /foodgram-project-react/infra:

```
docker-compose up -d --build
```

3. Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

4. Загрузить статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

5. Заполнить базу тестовыми данными:

```
docker-compose exec backend python manage.py loaddata dump.json
```

Теперь приложение будет доступно в браузере по адресам: localhost и localhost/admin/

Данные для тестового входа в админку:
Логин: a@ya.ru
пароль: 123
