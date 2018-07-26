import psycopg2

import settings


def db_connect():
    return psycopg2.connect(dbname=settings.db_name, user=settings.user,
                            password=settings.password, port=settings.port, host=settings.host)


def db_exec(cursor, command):
    try:
        cursor.execute(command)
    except Exception as e:
        print e


def create_tables(cursor):
    db_exec(cursor, open('create_tables.sql', 'r').read())


def fill_tables(cursor):
    db_exec(cursor, open('fill_tables.sql', 'r').read())


def add_item_to_order(cursor, order_id, good_id):
    # default quantity will be set to 42
    db_exec(cursor, """ INSERT INTO order_items(order_id, good_id, quantity) VALUES (%s, %s, 42)"""
            % (order_id, good_id))


def remove_item_from_order(cursor, order_id, good_id):
    db_exec(cursor, """DELETE FROM order_items where order_id=%s AND good_id=%s"""
            % (order_id, good_id))


def update_item_quantity(cursor, quantity, order_id, good_id):
    db_exec(cursor,
            """UPDATE order_items SET quantity=%s where order_id=%s AND good_id=%s"""
            % (quantity, order_id, good_id))


def get_all_goods(cursor):
    db_exec(cursor, open('select_all_goods.sql', 'r').read())
    return cursor.fetchall()


def drop_tables(cursor):
    db_exec(cursor, open('drop_tables.sql', 'r').read())


try:
    with db_connect() as conn:
        with conn.cursor() as cur:
            drop_tables(cur)
            create_tables(cur)
            fill_tables(cur)
            remove_item_from_order(cur, 2, 2)
            add_item_to_order(cur, 2, 1)
            update_item_quantity(cur, 50, 2, 1)

            # save all goods to text file
            all_goods = get_all_goods(cur)
            with open('all_goods.txt', 'w') as result_file:
                result_file.write('Name\tSurname\t\tProduct\t\tVendor\n')
                for item in all_goods:
                    result_file.write('\t'.join(item) + '\n')
except psycopg2.Error as e:
    print "unable to connect to the database"
    print e
