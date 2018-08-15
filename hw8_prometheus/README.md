# Домашнее задание 8: описание выполненной работы

## Задача:
```text
Установить и настроить Prometheus.  
Поставить стандартный экспортер - node_exporter.
```

## Используемые в работе файлы
* [node_exporter.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/node_exporter.ini) - конфигурационный файл supervisord для запуска node_exporter
* [prometheus.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/prometheus.ini) - конфигурационный файл supervisord для запуска Prometheus
* [uwsgi_exporter.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/uwsgi_exporter.ini) - конфигурационный файл supervisord для запуска uwsgi_exporter

## Ход работы
### 1) Настройка Prometheus и Node Exporter
```bash
# установка Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.3.2/prometheus-2.3.2.linux-amd64.tar.gz
tar -zxvf prometheus-2.3.2.linux-amd64.tar.gz

# установка node_exporter
wget  https://github.com/prometheus/node_exporter/releases/download/v0.16.0/node_exporter-0.16.0.linux-amd64.tar.gz
tar -zxvf node_exporter-0.16.0.linux-amd64.tar.gz
```

Далее необходимо добавить таргеты (хост:порт) для мониторинга Prometheus.  
Для этого нужно отредактировать файл ```prometheus-2.3.2.linux-amd64/prometheus.yml```.  
Добавим таргеты для мониторинга самого Prometheus (``` localhost:9090```) и экспортера node_exporter (```localhost:9100```).
```bash
vi prometheus-2.3.2.linux-amd64/prometheus.yml
```
```yaml
...
static_configs:
  - targets: ['localhost:9100','localhost:9090']
...
```

Проверим, что установка прошла успешно. Для этого запустим Prometheus и node_exporter:
```bash
# запуск Prometheus и node_exporter в фоновом режиме
./node_exporter-0.16.0.linux-amd64/node_exporter &
./prometheus-2.3.2.linux-amd64/prometheus  --config.file=prometheus-2.3.2.linux-amd64/prometheus.yml &

# проверка, что сервисы запущены успешно
ps aux | grep 9090
ps aux | grep 9100
```

Далее необходимо добавить 2 дешборда в сервис Grafana, первый должен отвечать за мониторинг самого Prometheus,  
второй - за мониторирнг таргета с установленным node_exporter (в данном случае они совпадают).
Сделать это можно по инструкции из задания: https://gitlab.com/tfs_s18_admin/homework/tree/master/materials/class08 .

### 2) Запуск prometheus и node_exporter в supervisord
Для запуска prometheus и node_exporter через supervisord, сначала остановим запущенные ранее сервисы.
```bash
sudo kill -9 `sudo lsof -t -i:9100`
sudo kill -9 `sudo lsof -t -i:9090`
```

Подключим конфигурационные файлы для указанных сервисов к supervisor.  
Для этого сначала перейдём в каталог ```/etc/supervisord.d/``` 
```bash
cd /etc/supervisord.d/
```

Теперь создадим здесь 2 файла: [node_exporter.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/node_exporter.ini) и [prometheus.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/prometheus.ini).  
В них описана конфигурация для supervisord, согласно которой нужно обслуживать данные сервисы.

Запустим сервисы при помощи supervisord:
```bash
sudo supervisorctl start prometheus
sudo supervisorctl start node_exporter
```

### 3) Подключение экспортера для uWSGI
Для подключения экспортера uWSGI, его необходимо сначала загрузить и распаковать.  
Данная процедура аналогична установке node_exporter.
```bash
wget https://github.com/timonwong/uwsgi_exporter/releases/download/v0.7.0/uwsgi_exporter-0.7.0.linux-amd64.tar.gz
tar -zxvf uwsgi_exporter-0.7.0.linux-amd64.tar.gz
```

Далее необходимо снова перейти в каталог с конфигурационными файлами supervisord и внести в него небольшие правки.  
Первым делом обновим former.ini, добавив к его команде запуска сделующие аргументы командной строки:
```bash
...
    --stats "127.0.0.1:1717"
    --stats-http
...
```
Это необходимо для того, чтобы uWSGI приложение начало отправлять метрики.

Затем добавим конфигурационный файл для запуска uwsgi_exporter. Его содержание приведено в   [uwsgi_exporter.ini](https://github.com/SK1995/tfs-admin/blob/hw8_prometheus/hw8_prometheus/uwsgi_exporter.ini).

Последним шагом необходимо обновить prometheus.yml, добавив туда новый таргет для мониторинга (9117 - стандартный порт для uwsgi_exporter):
```yaml
static_configs:
  - targets: ['localhost:9100','localhost:9090', 'localhost:9117']
```

Конфигурация supervisor завершена, теперь необходимо его перезапустить:
```bash
sudo supervisorctl reread
sudo supervisorctl update
```

## Результаты
В результате работы были добавлены 3 таргета для мониторинга Prometheus, для двух из них созданы дешборды в сервисе Grafana.  
Подключённые таргеты можно посмотреть по данной ссылке: http://s-27.fintech-admin.m1.tinkoff.cloud:9090/targets .