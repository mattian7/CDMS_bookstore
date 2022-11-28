import psycopg2
import logging
from be.model import error
from be.model import db_conn

class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 为不在store_id中的book_id新建数据，并写好书籍数量book_num
    def add_book(self, user_name, store_id, book_id, book_num):
        try:
            if not self.user_id_exist(user_name):
                return error.error_non_exist_user_id(user_name)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.conn.execute("select title from Book where Book.book_id=bookid")
            for tuple in self.conn.fetchall():
                book_name = tuple[0]
            values = [store_id, book_id, book_name, book_num]
            self.conn.execute("INSERT INTO Books_in_store (store_id, book_id, book_name, book_num)"
                              "VALUES (%s, %s, %s, %s)", values)
            self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_book_num: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("select title from Book where Book.book_id=bookid")
            for tuple in self.conn.fetchall():
                book_name = tuple[0]
            values = [store_id, book_id, book_name, add_book_num]
            self.conn.execute("UPDATE Books_in_store SET book_num = book_num + ? "
                              "WHERE store_id = ? AND book_id = ?", (add_stock_level, store_id, book_id))
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"