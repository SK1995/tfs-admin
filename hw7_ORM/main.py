import sys

from models import db, Customer, Order, Good, OrderItem
import queries

TABLES = [Customer, Order, Good, OrderItem]


def fill_db():
    Customer.insert({'first_nm': 'first name', 'last_nm': 'last name'}).execute()
    Good.insert({'vendor': 'vendor', 'name': 'name', 'description': 'description'}).execute()

    order = Order(order_dttm='1999-01-08', status='delivered')
    order.cust_id = Customer.select().first()
    order.save()

    order_item = OrderItem()
    order_item.good_id = Good.select().first()
    order_item.order_id = Order.select().first()
    order_item.save()


try:
    db.connect()
    db.drop_tables(TABLES)
    db.create_tables(TABLES)
    fill_db()

    test_customer = Customer()
    test_customer.first_nm = 'first_nm'
    test_customer.last_nm = 'last_nm'
    test_customer.save()

    good = Good()
    good.vendor = 'vendor'
    good.name = 'name'
    good.description = 'description'
    good.save()

    order = Order(order_dttm='1999-01-09', status='unknown')
    order.cust_id = test_customer
    order.save()

    queries.add_item_to_order(good, order)
    queries.remove_item_form_order(good,order)
    # write all goods to a text file
    with open('get_all_goods.txt', 'w') as f:
        f.write(str(queries.get_all_goods()))

except Exception as e:
    print >> sys.stderr, "unable to connect to the database: {}".format(e)
