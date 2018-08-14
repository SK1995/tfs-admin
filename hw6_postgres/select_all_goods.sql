SELECT DISTINCT first_nm, last_nm, name, vendor FROM orders ord
  INNER JOIN customers cst on ord.cust_id = cst.cust_id
  INNER JOIN order_items ord_itm on ord.order_id = ord_itm.order_id
  INNER JOIN goods g on ord_itm.good_id = g.good_id