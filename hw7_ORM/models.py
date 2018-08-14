from peewee import *

import settings

db = PostgresqlDatabase(database=settings.db_name,
                        user=settings.user,
                        password=settings.password,
                        host=settings.host,
                        port=settings.port)


class Customer(Model):
    cust_id = PrimaryKeyField()
    first_nm = CharField(max_length=100)
    last_nm = CharField(max_length=100)

    class Meta:
        database = db
        db_table = 'customers'


class Order(Model):
    order_id = PrimaryKeyField()
    cust_id = ForeignKeyField(model=Customer, field='cust_id')
    order_dttm = DateTimeField()
    status = CharField(max_length=20)

    class Meta:
        database = db
        db_table = 'orders'


class Good(Model):
    good_id = PrimaryKeyField()
    vendor = CharField(max_length=100)
    name = CharField(max_length=100)
    description = CharField(max_length=300)

    class Meta:
        database = db
        db_table = 'goods'


class OrderItem(Model):
    order_item_id = PrimaryKeyField()
    good_id = ForeignKeyField(model=Good, field='good_id')
    order_id = ForeignKeyField(model=Order, field='order_id')
    quantity = IntegerField(default=42)

    class Meta:
        db_table = 'order_items'
        database = db
