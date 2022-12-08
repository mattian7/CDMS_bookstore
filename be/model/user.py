import jwt
import time
import logging
import psycopg2
from be.model import error
from be.model import db_conn


# encode a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }


def jwt_encode(user_id: str, terminal: str) -> str:
    encoded = jwt.encode(
        {"user_id": user_id, "terminal": terminal, "timestamp": time.time()},
        key=user_id,
        algorithm="HS256",
    )
    return encoded.encode("utf-8").decode("utf-8")


# decode a JWT to a json string like:
#   {
#       "user_id": [user name],
#       "terminal": [terminal code],
#       "timestamp": [ts]} to a JWT
#   }
def jwt_decode(encoded_token, user_id: str) -> str:
    decoded = jwt.decode(encoded_token, key=user_id, algorithms="HS256")
    return decoded


class User(db_conn.DBConn):
    token_lifetime: int = 3600  # 3600 second

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def __check_token(self, user_id, db_token, token) -> bool:
        try:
            if db_token != token:
                return False
            jwt_text = jwt_decode(encoded_token=token, user_id=user_id)
            ts = jwt_text["timestamp"]
            if ts is not None:
                now = time.time()
                if self.token_lifetime > now - ts >= 0:
                    return True
        except jwt.exceptions.InvalidSignatureError as e:
            logging.error(str(e))
            return False

    def register(self, user_id: str, password: str):
        try:
            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            values = [[user_id, password, 0, token, terminal]]
            sql = "insert into User1 (user_id, password, balance, token, terminal) values (%s, %s, %s, %s, %s)"
            self.conn.executemany(sql, values)
        except psycopg2.Error:
            return error.error_exist_user_id(user_id)
        return 200, "ok"

    def check_token(self, user_id: str, token: str) -> (int, str):
        sql = "select token  from User1 where user_id= %s"
        cursor = self.conn.execute(sql, (user_id,))
        row = self.conn.fetchone()
        if row is None:
            return error.error_authorization_fail()
        db_token = row[0]
        if not self.__check_token(user_id, db_token, token):
            return error.error_authorization_fail()
        return 200, "ok"

    def check_password(self, user_id: str, password: str) -> (int, str):
        sql = "select password from User1 where user_id = %s"
        cursor = self.conn.execute(sql, (user_id,))
        row = self.conn.fetchone()
        if row is None:
            return error.error_authorization_fail()

        if password != row[0]:
            return error.error_authorization_fail()

        return 200, "ok"

    def login(self, user_id: str, password: str, terminal: str) -> (int, str, str):
        token = ""
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message, ""

            token = jwt_encode(user_id, terminal)
            self.conn.execute(
                "UPDATE User1 set token= '%s' , terminal = '%s' where user_id = '%s'" % (token, terminal, user_id)
            )

            if self.conn.rowcount == 0:
                return error.error_authorization_fail() + ("",)
        except psycopg2.IntegrityError as e:
            return 528, "{}".format(str(e)), ""

        return 200, "ok", token

    def logout(self, user_id: str, token: str) -> bool:
        try:
            code, message = self.check_token(user_id, token)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            dummy_token = jwt_encode(user_id, terminal)

            self.conn.execute(
                "UPDATE User1 set token= '%s' , terminal = '%s' where user_id = '%s'" % (dummy_token, terminal, user_id)
            )
            if self.conn.rowcount == 0:
                return error.error_authorization_fail()

            # self.conn.commit()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def unregister(self, user_id: str, password: str) -> (int, str):
        try:
            code, message = self.check_password(user_id, password)
            if code != 200:
                return code, message
            sql = "delete from User1 where user_id = %s"
            cursor = self.conn.execute(sql, (user_id,))
            # if self.conn.rowcount == 1:
            #     self.conn.commit()
            # else:
            #     return error.error_authorization_fail()
            if self.conn.rowcount != 1:
                return error.error_authorization_fail()
        except psycopg2.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        try:
            code, message = self.check_password(user_id, old_password)
            if code != 200:
                return code, message

            terminal = "terminal_{}".format(str(time.time()))
            token = jwt_encode(user_id, terminal)
            self.conn.execute("update User1 set password = '%s', token = '%s', terminal = '%s'where user_id = '%s'" %(new_password, token, terminal, user_id))
            if self.conn.rowcount == 0:
                return error.error_authorization_fail()

            # self.conn.commit()
        except psycopg2.IntegrityError as e:
            return 528, "{}".format(str(e))
        return 200, "ok"

    def whole_content_search(self, sub_content: str, store_id=None):
        try:
            if store_id is None:
                self.conn.execute("select book_id from Book where tscontent @@ to_tsquery('%s');"%sub_content)
            else:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
                else:
                    sql = "select book_id from Book where tscontent @@ to_tsquery('simple',%s) and book_id in (select book_id from Store where store_id = %s);"
                    self.conn.execute(sql, (sub_content, store_id))
        except psycopg2.Error as e:
            print(e)
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"

    def params_search(self, title=None, author=None, tags=None, store_id=None):
        flag = (title is None) & (author is None) & (tags is None) & (store_id is None)
        have_restrict = 0
        try:
            values = []
            if flag == 1:
                sql = "select title from Book"
            else:
                sql = "select title from Book where"

            if store_id is not None:
                sql += " book_id in (select book_id from Store where store_id = %s)"
                values.append(store_id)
                have_restrict = 1

            if title is not None:
                if have_restrict == 0:
                    sql += " title = %s"
                else:
                    sql += " and title = %s"
                values.append(title)
                have_restrict = 1

            if author is not None:
                if have_restrict == 0:
                    sql += " author = %s"
                else:
                    sql += " and author = %s"
                values.append(author)
                have_restrict = 1

            if tags is not None:
                if have_restrict == 0:
                    sql += " position (%s in Book.tags)>0"
                else:
                    sql += " and position (%s in Book.tags)>0"
                values.append(tags)

            if store_id is not None:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
                else:
                    self.conn.execute(sql, values)
            else:
                self.conn.execute(sql, values)
        except psycopg2.Error as e:
            print(e)
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(e)
            return 530, "{}".format(str(e))
        return 200, "ok"