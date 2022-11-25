import logging
import os
import sqlite3 as sqlite


class Store:
    database: str

    def __init__(self, db_path):
        self.database = os.path.join(db_path, "be.db")
        self.init_tables()

    def init_tables(self):
        try:
            conn = self.get_db_conn()
            conn.execute(
                "CREATE TABLE IF NOT EXISTS User("
                "user_name TEXT PRIMARY KEY,"  # 用户名
                "pwd varchar(15) ,"  # 密码
                "balance INTEGER,"  # 余额
                "token TEXT,"  # token
                "terminal TEXT"  # 端口
                ")"
            )
            conn.execute("INSERT INTO User values(?,?,?,?,?)",
                         ('test_id', 'test_pwd', 100, 'test_token', 'test_terminal'))
            conn.execute("INSERT INTO User values(?,?,?,?,?)",
                         ('test_id_2', 'test_pwd_2', 1000, 'test_token_2', 'test_terminal_2'))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS Book( "
                "book_id TEXT PRIMARY KEY,"  # 书本编号
                "title TEXT,"  # 书名
                "author TEXT,"  # 书本信息
                "publisher TEXT,"
                "original_title TEXT,"
                "translator TEXT,"
                "pub_year TEXT,"
                "pages INTEGER,"
                "price INTEGER,"
                "currency_unit TEXT,"
                "binding TEXT,"
                "isbn TEXT,"
                "author_intro TEXT,"
                "book_intro text,"
                "content TEXT,"
                "tags TEXT,"
                "picture BLOB"
                ")"
            )
            conn.execute("INSERT INTO Book values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                'book1', '霸王别姬', '李碧华', '新星出版社', '无', '无', '1', 235, 30, '1', '1', '1', '1', '1', '1', '1', '1'))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS Store("
                "store_id INTEGER PRIMARY KEY,"  # 店铺编号
                "owner TEXT,"  # 卖家user_name
                "FOREIGN KEY(owner) REFERENCES User(user_name)"
                ")"
            )
            conn.execute("INSERT INTO Store values(?,?)", (1, 'test_id'))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS Books_in_store( "
                "store_id INTEGER,"  # 店铺编号
                "book_id TEXT,"  # 书本编号
                "book_name TEXT,"  # 书名
                "book_num INTEGER,"  # 在售数量，完成一次订单后数量-1
                "FOREIGN KEY(store_id) REFERENCES Store(store_id),"
                "FOREIGN KEY(book_id) REFERENCES Book(book_id),"
                "FOREIGN KEY(book_name) REFERENCES Book(title),"
                "PRIMARY KEY(store_id, book_id)"
                ")"
            )
            conn.execute("INSERT INTO Books_in_store values(?,?,?,?)", (1, 'book1', '霸王别姬', 10))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS Orders( "
                "order_id INTEGER PRIMARY KEY,"  # 订单编号
                "seller TEXT,"  # 卖家
                "buyer TEXT,"  # 买家
                "status INTEGER,"  # 0为未付款（*这里可以不要 如果我们后面写的是点击购买后直接扣款就直接进入状态1），
                # 1为以付款未发货（买家付款后，商家填入物流前），
                # 2为已发货未收货（商家填入物流后，买家确认收货前），3为已收货完成订单 
                "time TEXT,"  # 下单时间，格式为 "YYYY-MM-DD HH:MM:SS.SSS" 的日期
                "book_id TEXT,"  # 书本编号
                "price INTEGER,"  # 书本价格
                "FOREIGN KEY(seller) REFERENCES Store(owner),"
                "FOREIGN KEY(buyer) REFERENCES User(user_name),"
                "FOREIGN KEY(book_id) REFERENCES Book(book_id)"
                ")"
            )
            conn.execute("INSERT INTO Orders values(?,?,?,?,?,?,?)",
                         (1, 'test_id', 'test_id_2', 3, '2022-11-25 23:00:50.000', 'book1', 10))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS User_order("
                "user_name TEXT,"  # 用户名
                "order_id INTEGER PRIMARY KEY,"  # 订单号
                "FOREIGN KEY(user_name) REFERENCES User(user_name),"
                "FOREIGN KEY(order_id) REFERENCES Orders(order_id)"
                ")"
            )
            conn.execute("INSERT INTO User_order values(?,?)", ('test_id', 1))

            conn.execute(
                "CREATE TABLE IF NOT EXISTS User_store("
                "user_name TEXT,"  # 用户名
                "store_id INTEGER PRIMARY KEY,"  # 店铺号
                "FOREIGN KEY(user_name) REFERENCES User(user_name),"
                "FOREIGN KEY(store_id) REFERENCES Store(store_id)"
                ")"
            )
            conn.execute("INSERT INTO User_store values(?,?)", ('test_id', 1))

            conn.commit()
        except sqlite.Error as e:
            logging.error(e)
            conn.rollback()

    def get_db_conn(self) -> sqlite.Connection:
        return sqlite.connect(self.database)


database_instance: Store = None


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.get_db_conn()
