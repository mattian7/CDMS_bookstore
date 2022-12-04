import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import db_conn
from be.model import error
from be.model import encryption
import psycopg2
from be.model.order_time import unpaid_order, check_order_time, remove_overtime_order
from be.model.order_list import Order
import time, datetime
import json


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 下单
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        # try:
        if not self.user_id_exist(user_id):  # 判断 user_id 是否存在
            return error.error_non_exist_user_id(user_id) + (order_id,)
        if not self.store_id_exist(store_id):  # 判断 store_id 是否存在
            return error.error_non_exist_store_id(store_id) + (order_id,)
        uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

        tupTime = time.time()
        structTime = time.localtime(tupTime)
        order_time = time.strftime('%Y-%m-%d %H:%M:%S', structTime)

        status = 0

        # 通过 store_id 在 Store 表里找到卖家
        self.conn.execute("SELECT owner from Store where store_id = '%s'" % (store_id))
        row = self.conn.fetchone()
        if row is None:
            return error.error_authorization_fail() + (order_id,)
        user_id1 = row[0]

        total_price = 0
        for book_id, count in id_and_count:
            self.conn.execute(
                "SELECT book_num from Books_in_store where store_id = '%s' and book_id = '%s'" % (store_id, book_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_non_exist_book_id(book_id) + (order_id,)
            book_num = row[0]

            # 库存不足
            if book_num < count:
                return error.error_stock_level_low(book_id) + (order_id,)

            # 更新 Books_in_store 表库存
            self.conn.execute("UPDATE Books_in_store set book_num = '%s' WHERE store_id = '%s' and book_id = '%s'" % (
            (book_num - count), store_id, book_id))

            # 计算总价
            self.conn.execute("SELECT price from Book where book_id = '%s'" % (book_id))
            row = self.conn.fetchone()
            one_price = row[0]
            total_price += count * one_price

        # 将新订单信息插入 Orders 表
        self.conn.execute(
            "INSERT INTO Orders(order_id, seller, buyer, store, status, time, book_id, price) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (uid, user_id1, user_id, store_id, status, order_time, book_id, total_price))

        order_id = uid
        # 将订单信息加入数组内，便于后续其他操作（例如定时取消未付款订单）
        # 而且这是全局数组，不用额外开启新线程，提高性能
        unpaid_order(order_id)

        # except psycopg2.Error:
        #     return error.error_invalid_order_id(order_id)

        return 200, "ok", order_id

    # 付款
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):

        try:
            # 获取订单信息
            self.conn.execute("SELECT * FROM Orders WHERE order_id = '%s'" % (order_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            seller_id = row[1]
            buyer_id = row[2]
            store_id = row[3]
            status = row[4]
            order_time = row[5]
            price = row[7]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            if status != 0:
                return error.error_invalid_order_status(order_id)  # error.py自定义函数

            # 如果订单已超时
            if check_order_time(order_time) == False:
                remove_overtime_order(order_id)
                order = Order()
                order.cancel_order(order_id)
                return error.error_invalid_order_id(order_id)

            # 如果订单未超时
            self.conn.execute("SELECT balance, password FROM User1 WHERE user_id = '%s'" % (buyer_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)

            balance = row[0]

            # 密码错误
            if password != row[1]:
                return error.error_authorization_fail()

            # 余额不足
            if balance < price:
                return error.error_not_sufficient_funds(order_id)

            self.conn.execute("SELECT owner FROM Store WHERE store_id = '%s'" % (store_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)
            seller_id = row[0]
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 付款成功
            self.conn.execute("UPDATE User1 set balance = '%s' WHERE user_id = '%s'" % ((balance - price), buyer_id))
            self.conn.execute("UPDATE Orders set status = 1 where order_id = '%s'" % (order_id))

            # 从未付款订单数组中删除
            remove_overtime_order(order_id)

        except psycopg2.Error:
            return error.error_exist_user_id(user_id)

        return 200, "ok"

    # 充值
    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            self.conn.execute("SELECT password,balance from User1 where user_id = '%s'" % (user_id))
            row = self.conn.fetchone()

            if row is None or row[0] != password:
                return error.error_authorization_fail()

            self.conn.execute("UPDATE User1 SET balance = '%s' WHERE user_id = '%s'" % ((row[1] + add_value), user_id))

            if self.conn.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

        except psycopg2.Error:
            return error.error_exist_user_id(user_id)

        return 200, "ok"

    # 收货
    def receive(self, user_id: str, password: str, order_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):  # 判断 user_id 是否存在
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):  # 判断 order_id 是否存在
                return error.error_invalid_order_id(order_id)

            self.conn.execute("SELECT password FROM User1 WHERE user_id = '%s'" % (user_id))
            row = self.conn.fetchone()
            if password != row[0]:  # 密码错误
                return error.error_authorization_fail()

            self.conn.execute(
                "SELECT order_id, seller, buyer, status, price FROM Orders WHERE order_id = '%s'" % (order_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            seller_id = row[1]
            buyer_id = row[2]
            status = row[3]
            total_price = row[4]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if status != 2:
                return error.error_invalid_order_status(order_id)
            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            # 订单状态改为已收货完成订单
            self.conn.execute("UPDATE Orders set status=3 WHERE order_id = '%s'" % (order_id))
            if self.conn.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

            # 给卖家余额加上
            self.conn.execute(
                "UPDATE User1 set balance = balance + '%s'  WHERE user_id = '%s'" % (total_price, seller_id))
            if self.conn.rowcount == 0:
                return error.error_non_exist_user_id(buyer_id)

        except psycopg2.Error:
            return error.error_exist_user_id(user_id)

        return 200, "ok"

    # 查询订单
    def query_order(self, user_id: str, order_id: str):
        try:
            if not self.user_id_exist(user_id):  # 判断 user_id 是否存在
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):  # 判断 order_id 是否存在
                return error.error_invalid_order_id(order_id)

            self.conn.execute(
                "SELECT order_id, seller, buyer, status, price, time, book_id FROM Orders WHERE order_id = '%s'" % (order_id))
            row = self.conn.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            seller_id = row[1]
            buyer_id = row[2]
            status = row[3]
            total_price = row[4]
            time = row[5]
            book = row[6]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            # idx = 'order_id:' + order_id + 'seller_id:' + seller_id + 'buyer_id:' + buyer_id + 'status:' + status + 'total_price:' + total_price + 'time:'+time+'book:'+book
            idx = {
                "order_id":order_id,
                "seller_id":seller_id,
                "buyer_id":buyer_id,
                "status":status,
                "total_price":total_price,
                "time":time,
                "book":book
            }
        except psycopg2.Error:
            return error.error_exist_user_id(user_id)

        return 200, json.dumps(idx)
