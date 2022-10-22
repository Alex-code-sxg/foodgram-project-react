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
### Заполните базу тестовыми данными:
```
docker-compose exec backend python manage.py loaddata dump.json
```
