<h1 align="left">Проект Foodgram</h1>

![example workflow](https://github.com/Alex-code-sxg/foodgram-project-react/actions/workflows/main.yml/badge.svg)

```
Перейдите в папку foodgram-project-react/infra
```
cd foodgram-project-react/infra
```

Выполните команду:
```
docker-compose up -d --build
```

### Выполните миграции:
```
docker-compose exec backend python manage.py migrate
```

### Загрузите статику:
```
docker-compose exec backend python manage.py collectstatic --no-input
```
