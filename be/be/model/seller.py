import psycopg2
import logging
from be.model import error
from be.model import db_conn
from be.model import user


class Seller(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    # 添加不存在的书
    def add_book(self, user_id: str, store_id: str, book_id: str, book_num: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.conn.execute("SELECT title FROM Book WHERE book_id = %s", (book_id,))
            book_name = self.conn.fetchone()

            values = [store_id, book_id, book_name, book_num]
            self.conn.execute("INSERT into Books_in_store (store_id, book_id, book_name, book_num)"
                              "VALUES (%s, %s, %s, %s)", values)

        except psycopg2.Error as e:
            print(e)
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 添加存在的书
    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_num: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("UPDATE Books_in_store SET book_num = book_num + %s "
                              "WHERE store_id = %s AND book_id = %s", (add_num, store_id, book_id))

        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        # try:
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if self.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)

        self.conn.execute("INSERT into Store (store_id, owner)"
                          "VALUES (%s, %s)", (store_id, user_id))

        # except psycopg2.Error as e:
        #     print(e)
        #     return 528, "{}".format(str(e))
        # except BaseException as e:
        #     print(e)
        #     return 530, "{}".format(str(e))
        return 200, "ok"