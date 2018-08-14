CREATE TABLE IF NOT EXISTS customers
(
  cust_id serial PRIMARY KEY,
  first_nm varchar(100),
  last_nm varchar(100)
);

CREATE TABLE IF NOT EXISTS orders
(
  order_id serial PRIMARY KEY,
  cust_id serial,
  order_dttm timestamp,
  status varchar(20),
  FOREIGN KEY (cust_id) REFERENCES customers (cust_id)
);

CREATE TABLE IF NOT EXISTS goods
(
  good_id serial PRIMARY KEY,
  vendor varchar(100),
  name varchar(100),
  description varchar(300)
);

CREATE TABLE IF NOT EXISTS order_items
(
  order_item_id serial PRIMARY KEY,
  order_id int,
  good_id int,
  quantity int,
  FOREIGN KEY (order_id) REFERENCES orders (order_id),
  FOREIGN KEY (good_id) REFERENCES goods (good_id)
);

