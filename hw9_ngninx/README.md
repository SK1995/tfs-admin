# Домашнее задание 9: описание выполненой работы 

## Задача
```
 Ознакомиться с веб-сервером nginx.
 Научиться собирать nginx c third-party модулем VTS.
```

## Используемые в работе файлы
* [1-test.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/1-test.conf) - конфигурационный файл nginx для перовго пукта задания
* [1-test_updated.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/1-test_updated.conf) - rонфигурационный файл nginx для второго пукта задания
* [default.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/default.conf) - конфигурационный файл nginx для перовго пукта задания
* [nginx.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/nginx.conf) - файл с базовой конфигурацией nginx

## Ход работы
### 1) Конфигурация простого статического сайта
```bash
# установка nginx
sudo rpm --import https://nginx.org/keys/nginx_signing.key
sudo rm -rf /etc/yum.repos.d/puppet5.repo
sudo echo "
[nginx.org]
name=Nginx official repo (binaries)
baseurl=http://nginx.org/packages/centos/$releasever/$basearch/
enabled=1

[nginx.org-src]
name=Nginx official repo (sources)
baseurl=http://nginx.org/packages/centos/7/SRPMS/
enabled=1

" > /etc/yum.repos.d/nginx.repo
sudo yum clean all && yum install -y nginx

# старт сервиса nginx
sudo systemctl enable start

# добавление nginx а автозапуск
sudo systemctl enable nginx
```

В дальнейшей работе будет требоваться работать с 80 портом, настраивая для него разные локейшоны.  
Поэтому сразу уберём их из стандартного конфигурационного файла ([nginx.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/nginx.conf)). 
Для этого из него необходимо вырезать данные строки:
```text
...        location / {
            ...
        }
 ...       
```

Добавим минимальный конфигурационный файл `/etc/nginx/conf.d/1-test.conf`, удовлетворяющий следующим критериям:
* имя сервера, на которое откликается сервер: `test-1`
* порт: `80`
* корень для сайта: `/var/www/test-1` 

Данный файл может выглядить следующим образом ([1-test.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/1-test.conf)):
```text
server 
{
    # настройка порта согласно условию
    listen       80;
    # настройка имени сервера согласно условию
    server_name test-1;
    # настройка корня, согласно условию
    root /var/www/test-1;
}
```

Теперь необходимо создать файл, который будет возвращаться в запросах на location по умолчанию.  
В nginx за это отвечает директива index.   
Её стандартное значение - `index index.html;`.
Создадим файл `index.html` для указанного root:

```bash
echo "Yohoo, it works" > /var/www/test-1/index.html
```

Выполним оставшуюся часть настройки из первого пукнта задания:
```bash
# добавляение прав SELinux на каталоги, ианче у пользователя Nginx Не будет прав читать файлы
sudo chcon -Rt httpd_sys_content_t /var/www

# Перезагружаем nginx, чтобы применить конифгурацию
sudo nginx -s reload
```

Чтобы сделать возможным обращение к виртуальным серверам по адресу `test-1` и `test-2`, отредактируем  
файл `/etc/hosts`, добавив туда следующие значения:
```bash
...
127.0.0.1  test-1 test-2
...
``` 

Проверяем выполненные настройки:
```bash
curl test-1 # Yohoo, it works
curl test-2 # Yohoo, it works
```
Для разделения адресов `test-1` и `test-2`, добавим ещё один конфигурационный файл по адресу `/etc/nginx/conf.d/default.conf`.
Его задачами будет:
* слушать подключения на 80м порту по умолчанию
* возвращение 404 с телом 'No <имя сервера> server config found на все запросы

Данный файл может выглядить так ([default.conf](https://github.com/SK1995/tfs-admin/blob/hw9_nginx/hw9_ngninx/default.conf))
```text
server {
    listen       80 default_server; #
    server_name  localhost;

    location / {
	default_type text/plain;
        return 404 'No $host server config found';
    }

    error_page   500 502 503 504  /50x.html;
    location = /50x.html {
        root   /usr/share/nginx/html;
    }
}
```
Директива `default_server` здесь отвечает за то, чтобы сделать данный сервер сервером по умолчанию  
для запросов на 80 порт.
Стоит также обратить внимание на директиву `default_type text/plain;`. 
Она необходима для того, чтобы страницу с текстовым ответом можно было получить не только через консольные утилиты  
вроде curl, но и через браузер. Она добавляет к ответу сервера заголовок `Content-type`, который позволяет его корректно интерпретировать.

Теперь при перезагрузке nginx получаем разные ответы по адресам `test-1` и `test-2`.

### 2) Сборка и запуск Nginx с VTS-модулем
Процесс сбокри и запуска Nginx c VTS-модулем описан в условии задания по адресу https://gitlab.com/tfs_s18_admin/homework/tree/master/materials/class09-ngx .
Перед выполнением данных шагов, описанных в нём, необходимо установить следующие пакеты:
```bash
sudo yum install redhat-lsb-core -y && sudo yum install rpm-build rpmdevtools -y
```

После выполнения указанных шагов, отдачу метрик можно проверить, перейдя по адресу `test-1/status`.
```bash
curl test-1/status
```
```text
# HELP nginx_vts_info Nginx info
# TYPE nginx_vts_info gauge
nginx_vts_info{hostname="s-27.fintech-admin.m1.tinkoff.cloud",version="1.14.0"} 1
# HELP nginx_vts_start_time_seconds Nginx start time
# TYPE nginx_vts_start_time_seconds gauge
nginx_vts_start_time_seconds 1535316664.064
# HELP nginx_vts_main_connections Nginx connections
# TYPE nginx_vts_main_connections gauge
nginx_vts_main_connections{status="accepted"} 4
nginx_vts_main_connections{status="active"} 1
nginx_vts_main_connections{status="handled"} 4
nginx_vts_main_connections{status="reading"} 0
nginx_vts_main_connections{status="requests"} 4
nginx_vts_main_connections{status="waiting"} 0
nginx_vts_main_connections{status="writing"} 1
# HELP nginx_vts_main_shm_usage_bytes Shared memory [ngx_http_vhost_traffic_status] info
# TYPE nginx_vts_main_shm_usage_bytes gauge
nginx_vts_main_shm_usage_bytes{shared="max_size"} 1048575
nginx_vts_main_shm_usage_bytes{shared="used_size"} 3518
nginx_vts_main_shm_usage_bytes{shared="used_node"} 1
# HELP nginx_vts_server_bytes_total The request/response bytes
# TYPE nginx_vts_server_bytes_total counter
# HELP nginx_vts_server_requests_total The requests counter
# TYPE nginx_vts_server_requests_total counter
# HELP nginx_vts_server_request_seconds_total The request processing time in seconds
# TYPE nginx_vts_server_request_seconds_total counter
# HELP nginx_vts_server_request_seconds The average of request processing times in seconds
# TYPE nginx_vts_server_request_seconds gauge
# HELP nginx_vts_server_request_duration_seconds The histogram of request processing time
# TYPE nginx_vts_server_request_duration_seconds histogram
# HELP nginx_vts_server_cache_total The requests cache counter
# TYPE nginx_vts_server_cache_total counter
nginx_vts_server_bytes_total{host="localhost",direction="in"} 667
nginx_vts_server_bytes_total{host="localhost",direction="out"} 639
nginx_vts_server_requests_total{host="localhost",code="1xx"} 0
nginx_vts_server_requests_total{host="localhost",code="2xx"} 0
nginx_vts_server_requests_total{host="localhost",code="3xx"} 0
nginx_vts_server_requests_total{host="localhost",code="4xx"} 3
nginx_vts_server_requests_total{host="localhost",code="5xx"} 0
nginx_vts_server_requests_total{host="localhost",code="total"} 3
nginx_vts_server_request_seconds_total{host="localhost"} 0.000
nginx_vts_server_request_seconds{host="localhost"} 0.000
nginx_vts_server_cache_total{host="localhost",status="miss"} 0
nginx_vts_server_cache_total{host="localhost",status="bypass"} 0
nginx_vts_server_cache_total{host="localhost",status="expired"} 0
nginx_vts_server_cache_total{host="localhost",status="stale"} 0
nginx_vts_server_cache_total{host="localhost",status="updating"} 0
nginx_vts_server_cache_total{host="localhost",status="revalidated"} 0
nginx_vts_server_cache_total{host="localhost",status="hit"} 0
nginx_vts_server_cache_total{host="localhost",status="scarce"} 0
nginx_vts_server_bytes_total{host="*",direction="in"} 667
nginx_vts_server_bytes_total{host="*",direction="out"} 639
nginx_vts_server_requests_total{host="*",code="1xx"} 0
nginx_vts_server_requests_total{host="*",code="2xx"} 0
nginx_vts_server_requests_total{host="*",code="3xx"} 0
nginx_vts_server_requests_total{host="*",code="4xx"} 3
nginx_vts_server_requests_total{host="*",code="5xx"} 0
nginx_vts_server_requests_total{host="*",code="total"} 3
nginx_vts_server_request_seconds_total{host="*"} 0.000
nginx_vts_server_request_seconds{host="*"} 0.000
nginx_vts_server_cache_total{host="*",status="miss"} 0
nginx_vts_server_cache_total{host="*",status="bypass"} 0
nginx_vts_server_cache_total{host="*",status="expired"} 0
nginx_vts_server_cache_total{host="*",status="stale"} 0
nginx_vts_server_cache_total{host="*",status="updating"} 0
nginx_vts_server_cache_total{host="*",status="revalidated"} 0
nginx_vts_server_cache_total{host="*",status="hit"} 0
nginx_vts_server_cache_total{host="*",status="scarce"} 0
```

Можно также посмотреть список всех модулей, с которыми был скомпилирован nginx при помощи  
команды `nginx -V`.

### Результаты
Результаты работы можно проверить на виртуальной машине  ```s-27.fintech-admin.m1.tinkoff.cloud```.




