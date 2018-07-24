# Домашнее задание 5: описание выполненой работы 

## Задача
```
"Пощупать" элементарное веб-приложение на Python, работающее под uwsgi. 
 Научиться поднимать uwsgi-приложение под supervisor-ом.
```

## Используемые в работе файлы
* [former.ini](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/former.ini) - rонфигурационный файл для supervisor
* [index.html](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/index.html) - форма для обслуживания веб-сервером
* [webrunner.py](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/webrunner.py) - бизнес-логика wsgi-приложения.

## Ход работы
### 0) Подготовка окружения
```bash
#установка необходимых пакетов
sudo yum install -y uwsgi uwsgi-plugin-python supervisor

#обновление репозитория с заданием/root/homework
cd /root/homework && git pull origin master

#копирование компонент веб-приложения в новый каталог
mkdir -p /opt/webcode/
cp -R /root/homework/materials/class05/src/former /opt/webcode
```

### 1) Запуск приложения
```
uwsgi --plugins=python --http-socket=0.0.0.0:80 --wsgi-file /opt/webcode/former/process/webrunner.py --static-map /form=/opt/webcode/former/form/index.html --processes=5 --master --pidfile=/tmp/formdig.pid --vacuum --max-requests=5000
```
Данная команда запускает на виртуальной машине сервер, логика работы которого расположена в файле [webrunner.py](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/webrunner.py). 
Проверим, что сервер доступен:
```bash
curl 0.0.0.0:80
```
В ответ получаем сообщение от сервера.
```text
Method: GET
Get content: /
Post content: 
```
Сервер запущен успешно.

### 2) Запуск приложения при помощи supervisor
```bash
#включение сервиса supervisord и настройка его автозапуска
systemctl enable supervisor
systemctl start supervisor

#создание каталога для логов сервера
mkdir -p /var/log/webapps

#подключение файла с конфигурацией приложения former к supervisor
cp /root/homework/materials/class05/src/former.ini /etc/supervisord.d/

#обновление конфигурационного файла supervisor, перезапуск приложений, для которых конфигурация изменилась
supervisorctl reread
supervisorctl update
```

### 3) Изменения метода отправки 
Для изменения метода отправки формы с POST на GET, внесём следующие изменения в код формы в [index.html](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/index.html):
```html
...
<form action="/process" method="GET">
...
```
Обновлённый вариант index.html [доступен по данной ссылке](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/index_new.html).

Перезапустим supervisor и проверим, что метод действительно изменился:
```bash
service supervisord restart
```
Теперь при нажатии на кнопку submit получаем страницу следующего содержания:
```text
Method: GET
Get content: /process?Name=1&Age=1
Post content:
``` 


В заключение проверим, что supervisord настроен корретно и готов перезапустить приложение в случае ошибки.
Для этого эстренно завершим приложение и обратимся к нему с небольшой задержкой:
```bash
#сервер запущен на 80 порту, пошлём ему сигнал SIGKILL для аварийного завершения
#затем подождём 5 секунд, чтобы убедиться, что supervisor успел перезапустить сервер.
kill -9 `lsof -t -i:80` && sleep 5
```
```bash
#проверка доступности
curl 0.0.0.0:80
```
Получаем ответ
```text
Method: GET
Get content: /process?Name=1&Age=1
Post content:
```

```bash
#Проверим логи supervisor
tail /var/log/supervisor/supervisord.log
```
```text
2018-07-24 19:09:47,869 INFO exited: former (terminated by SIGKILL; not expected)
2018-07-24 19:09:48,876 INFO spawned: 'former' with pid 30899
2018-07-24 19:09:48,896 INFO success: former entered RUNNING state, process has stayed up for > than 0 seconds (startsecs)
```
Приложение корректно настроено и переживает аварийное завершение.

### 4) Разбор конфигурационных файлов
В данной части будут разобраны конфигурационные файлы, команды и код приложения former.

#### 4.1 Разбор команды запуска сервера
Команда для запуска сервера выглядит следующим образом:
```bash
uwsgi --plugins=python --http-socket=0.0.0.0:80 --wsgi-file /opt/webcode/former/process/webrunner.py --static-map /form=/opt/webcode/former/form/index.html --processes=5 --master --pidfile=/tmp/formdig.pid --vacuum --max-requests=5000
```
Разберём каждый из флагов, с которым сервер запускается:
* --plugins=python  
Запуск с поддержкой плагина python. 
Необходимо для запуска кода python-приложений.
* --http-socket=0.0.0.0:80  
Привязка к заданному UNIX/TCP соекту, используя протокол http.
* --wsgi-file /opt/webcode/former/process/webrunner.py  
Путь к wsgi-файлу на языке python, который будет обслуживать сервер. 
* --static-map  /form=/opt/webcode/former/form/index.html  
Настройка URL. Отдача файла index.html при запросе адреса /form.
* --processes=5  
Запуск указанного количества процессов для сервера
* --master  
Влючение мастер-процесса. Необходимо для благополучного перезапуска приложения и завершения зависших процессов.
* --pidfile=/tmp/formdig.pid  
* --vacuum  
При указании данной опции, uwsgi пытается удалить созданные сокеты и файлы при завершении работы.
* --max-requests=5000  
Перезапуск worker-процессов после обслуживания заданного количества запросов.

#### 4.2 Разбор конфигурационного файла
Рассмотрим файл [former.ini](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/former.ini)
* [program:former]  
Создание записи о новом приложении с именем former.
* command  
Команда, которая будет запущена при старте приложения.
* stopsignal=QUIT   
Сигнал, посылаемый приложению, когда его необходимо завершить
* autostart=true  
Если флаг установлен в true, то приложение запускается вместе с запуском демона supervisor
* startretries=10  
Количество попыток, которые предпримет supervisor перед тем, как пометит процесс как FAIL.
* startsecs=0  
Количество секунд, которое программа должа проработать, чтобы её запуск считался успешным.
Значение 0 означает, что конкретное время работы программы не определено.
* stopwaitsecs=10  
Количество секунд, при котором supervisord будет ждать  от приложения сигнал SIGHLD.
Не дождавшись сигнала, supervisord попробует убить приложение через SIGKILL.
* stopasgroup=true  
Заставляет supervisord отправлять сигнал остановки всем дочерним процессам приложения.
* stdout_logfile=/var/log/webapps/former_stdout.log  
Файл для хранения stdout приложения
*stdout_logfile_maxbytes=60MB  
Максимальный размер stdout_logfile перед его ротацией.
* stdout_logfile_backups=4
Установка количества файлов, хранимых при ротации stdout_logfile.
* stdout_capture_maxbytes=4MB  
Максимально разрешённое количество байт при чтении stdout процесса.
* stderr_logfile=/var/log/webapps/former_stderr.log  
Файл для хранения stderr приложения.
* Максимальный размер stderr_logfile перед его ротацией.
* stderr_logfile_backups=4  
Установка количества файлов, хранимых при ротации stderr_logfile.
* stderr_capture_maxbytes=4MB  
Максимально разрешённое количество байт при чтении stderr процесса.

#### 4.3 Разбор бизнес-логики приложения
Расмотрим файл [webrunner.py](https://github.com/SK1995/tfs-admin/blob/hw5_supervisord/hw5_supervisord/webrunner.py) построчно.  
Т. к. это wsgi-приложение, для его корректной работы должны быть определены функция-обработчик запроса, и переменные окружения, с которыми функция будет взаимодействовать.

Сначала происходит указание пути к интерпретатору python:
```python
  #!/usr/bin/python
```
Затем импортируется функция parse_qs для работы с quiry string:
```python
from cgi import parse_qs
```

Затем определяется функция application(env, start_response), в которой сосредоточена логика работы приложения.
Именно эта функция вызывается при запуске uwsgi по-умолчанию
```python
def application(env, start_response)
```

Затем происходит вызов функции-обработчика запроса start_response.  
Вызов данной функции обязателен для всех wsgi приложений.  
Она представляет из себя объект типа callable и является ответственной за
 установку кода и заголовков ответа сервером.  
```python
    start_response('200 OK', [('Content-Type','text/plain')])
```

Затем происходит чтение переменных окружения:
```python
    wsgi_content = env["wsgi.input"].read(0)
    request_uri_content = env["REQUEST_URI"]
    request_method_content = env["REQUEST_METHOD"]
```

После этого происходит парсинг query string.  
Результат парсинга (d) в данном примере никак не обрабатываются.
```python
    d = parse_qs(wsgi_content)
```

Затем возвращается итерируемый объект (список),  
который потом при помощи uwsgi-сервера передаётся в ответе на запрос сервера.
```python
   return ["Method: " + request_method_content + "\n" +
        "Get content: " + request_uri_content + "\n" +
        "Post content: " + wsgi_content + "\n"]
```

### Результаты
Результаты работы можно проверить на виртуальной машине  ```s-27.fintech-admin.m1.tinkoff.cloud```.




