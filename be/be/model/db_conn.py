from be.model import store


class DBConn:
    def __init__(self):
        self.conn = store.get_db_conn()

    def user_id_exist(self, user_id):
        cursor = self.conn.execute("SELECT user_id FROM User1 WHERE user_id = %s", (user_id,))
        row = self.conn.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.conn.execute("SELECT book_id FROM Books_in_store WHERE store_id = %s AND book_id = %s", (store_id, book_id))
        row = self.conn.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.conn.execute("SELECT store_id FROM Store WHERE store_id = %s", (store_id,))
        row = self.conn.fetchone()
        if row is None:
            return False
        else:
            return True

    def order_id_exist(self, order_id):
        cursor = self.conn.execute("SELECT order_id FROM new_order WHERE order_id = %s", (order_id))
        row = self.conn.fetchone()
        if row is None:
            return False
        else:
            return True