from models import *


def add_item_to_order(good, order):
    order_item = OrderItem()
    order_item.order_id = order
    order_item.good_id = good
    order_item.save()


def remove_item_form_order(good, order):
    OrderItem.delete().where(OrderItem.good_id == order and OrderItem.good_id == good).execute()


def change_item_quantity(order_item, quantity):
    order_item.quantity = quantity
    order_item.save()


def get_all_goods():
    result_list = []
    for order_item in OrderItem.select():
        curr_custumer = order_item.order_id.cust_id
        result_list.append(
            {'name': order_item.good_id.name, 'vendor': order_item.good_id.vendor, 'quantity': order_item.quantity,
             'cust_name': "{} {}".format(curr_custumer.first_nm, curr_custumer.last_nm)})
    return result_list
