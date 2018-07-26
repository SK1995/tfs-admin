# Домашнее задание 6: описание выполненой работы 

## Задача
```
 Научиться устанавливать, запускать postgres.  
 Научиться выполнять базовые команды SQL из python.
 https://gitlab.com/tfs_s18_admin/homework/tree/master/materials/class06
```

## Используемые в работе файлы
* [main.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/main.py) - основная логика взаимодействия с БД.
* [settings.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/settings.py) - настройки подключения к БД.
* [select_all_goods.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/select_all_goods.sql) - запрос для выгрузки всех товаров всех заказов из БД.
* [create_tables.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/create_tables.sql) - запрос для создания тестовых полей в БД.
* [drop_tables.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/drop_tables.sql) - запрос для удаления тестовых полей из БД.
* [fill_tables.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/fill_tables.sql) - запрос для наполнения полей БД тестовыми данными.
* [all_goods.txt](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/all_goods.txt) - результат выгрузки запроса select_all_goods.sql в текстовый файл.


## Ход работы
### 0) Подготовка окружения
```bash
#установка необходимых пакетов
sudo yum install postgresql-server postgresql-contrib python-psycopg2 -y
```

### 1) Установка и запуск postgresql
```bash
#начальная установка кластера postgresql
sudo postgresql-setup initdb

#запуск и настройка автозагрузки демона postgresql при старте системы
sudo systemctl start postgresql
sudo systemctl enable postgresql
#проверка, что база данных успешно запущена
sudo netstat -tlpn | grep 5432
```

Далее необходимо открыть файл ```/var/lib/pgsql/data/postgresql.conf``` и изменить его,  
чтобы настроить параметры сервера согласно заданию
```text
...
shared_buffers = 512MB # настройка разделяемой памяти сервера
work_mem = 32MB        # настройка максимальной памяти для вычислительных процессов
port = 6789            # указание порта
listen_addresses = '*' # указание серверу слушать подключения со всех ip
...
```
Кроме того, при установке через yum, postgresql на CentOs 7 дополнительно создаёт свой  
сервис в systemd, который изменяет порт, указанный в конфигурационном файле.  
Конфигурация данного сервиса лежит в ```/lib/systemd/system/postgresql.service```, изменим его
```text
...
Environment=PGPORT=6789
...
```

Последним шагом настройки обновим ```/var/lib/pgsql/data/pg_hba.conf```, чтобы разрешить всем пользователям  
подключаться к серверу БД по паролю:
```bash
# IPv4 local connections:
host    all             all             all                     md5
```
Для вступления изменений в силу, перезапустим postgresql и systemd:
```bash
#обвновление конфигурационных файлов systemd 
systemctl daemon-reload

#отключение selinux и firewalld
setenforce 0
sudo service firewalld stop

#перезапуск postgres
systemctl restart postgresql

#проверка, что сервер успешно запустился
sudo netstat -tlpn | grep 6789
```

Обновим пароль для пользователя postgres, чтобы его в дальнейшем можно было использовать для подключения с паролем
```bash
su - postgres
psql -P 6789
ALTER USER postgres WITH PASSWORD 'postgres';
```

### 2) Создание БД
Подключимся к БД с новым паролем, создадим таблицу ```test_db``` для работы скриптов из задания:
```bash
su - postgres
psql -h 0.0.0.0 -U postgres -W
CREATE DATABASE test_db;
```
Проверить создание новой базы ```test_db``` можно при помощи команды ```\l``` ,  
находясь в интерфейсе утилиты ```psql```.

Вся дальнейшая работа с базой будет осуществляться при помощи скипта [main.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/main.py),  
написанного на языке python, c использованием драйвера ```psycopg2```.

Создание таблиц, необходимых в задании, описано в файле  [create_tables.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/create_tables.sql).  
Он используется в [main.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/main.py)в функции ```create_tables```.

Для удаления таблиц используется запрос из файла [drop_tables.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/drop_tables.sql),  
который вызывается в функции ```drop_tables```.

### 3) Написать функции добавления товара, удаления товара, изменения количества товара.
Запросы на добавление, удаление и обновление количества товара записаны напрямую в [main.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/main.py),  
т. к. они сравнительно невелеки и требуют параметризации.
Данные запросы выглядят следующим образом:
```sql
INSERT INTO order_items(order_id, good_id, quantity) VALUES (%s, %s, 42) --добавление нового товара в заказ
DELETE FROM order_items where order_id=%s AND good_id=%s                 -- удаление товара из заказа
UPDATE order_items SET quantity=%s where order_id=%s AND good_id=%s      -- обновление количества товара в заказе
```
Их вызовы обёрнуты в питоновские функции ```add_item_to_order```, ```remove_item_from_order``` и ```update_item_quantity``` соответственно.

### 4) Выгрузка всех товаров
Запрос для выгрузки всех товаров находися в файле [select_all_goods.sql](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/select_all_goods.sql).  
Он вызывается при помощи функции ```get_all_goods``` из [main.py](https://github.com/SK1995/tfs-admin/blob/hw6_postgres/hw6_postgres/main.py), после чего результаты записываются в текстовый файл. 
Данная часть происходит в участке кода, приведённом ниже:
```python
            # save all goods to text file
            all_goods = get_all_goods(cur)
            with open('all_goods.txt', 'w') as result_file:
                result_file.write('Name\tSurname\t\tProduct\t\tVendor\n')
                for item in all_goods:
                    result_file.write('\t'.join(item) + '\n')
```

### Результаты
Результаты работы можно проверить на виртуальной машине  ```s-27.fintech-admin.m1.tinkoff.cloud``` (все упомянутые в работе файлы лежат в каталоге ```/root/hw6_postgres```).  
Для запуска всех скриптов необходимо выполнить команду ```python main.py```.  
В результате выполнения с базой test_db будет выполнена следующая последовательность операций:
* очистка базы 
* создание полей из задания
* заполнение полей тестовыми данными
* добавление товара в заказ
* удаление товара из заказа
* изменение количества товара в заказе
* запрос всех товаров, запись результата в текстовый файл (````all_goods.txt````)




