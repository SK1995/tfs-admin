INSERT INTO customers(first_nm, last_nm) VALUES ('User1', 'LastName1');
INSERT INTO customers(first_nm, last_nm) VALUES ('User2', 'LastName2');

INSERT INTO orders(cust_id, order_dttm, status) VALUES (1, '2016-06-22 19:10:25', 'DELIVERED');
INSERT INTO orders(cust_id, order_dttm, status) VALUES (2, '2017-03-20 14:25:25', 'UNKNOWN');

INSERT INTO goods(vendor, name, description) VALUES ('Vendor1', 'ProductName1', 'Description1');
INSERT INTO goods(vendor, name, description) VALUES ('Vendor2', 'ProductName2', 'Description2');

INSERT INTO order_items(order_id, good_id, quantity) VALUES (1, 1, 42);
INSERT INTO order_items(order_id, good_id, quantity) VALUES (2, 2, 42);
