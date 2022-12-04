import psycopg2
import logging
from be.model import error
from be.model import db_conn
from be.model import user


class Search(db_conn.DBConn):

    def __init__(self):
        db_conn.DBConn.__init__(self)

    def params_search(self, title=None, author=None, price=None, tags=None, content=None, store_id=None):
        flag = (title is None) & (author is None) & (price is None) & (tags is None) & (content is None) & (
                store_id is None)
        have_restrict = 0
        try:
            values = []
            if flag == 1:
                sql = "select book_name from Book"
            else:
                sql = "select book_name from Book where"

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

            if price is not None:
                low_price = price[0]
                upper_price = price[1]
                if have_restrict == 0:
                    sql += " price >= %s and price <=%s"
                else:
                    sql += " and price >= %s and price <=%s"
                values.append(low_price, upper_price)
                have_restrict = 1

            if tags is not None:
                if have_restrict == 0:
                    sql += " tags = %s"
                else:
                    sql += " and tags = %s"
                values.append(tags)
                have_restrict = 1

            if tags is not None:
                if have_restrict == 0:
                    sql += " tags = %s"
                else:
                    sql += " and tags = %s"
                values.append(tags)

            if store_id is not None:
                if not self.store_id_exist(store_id):
                    return error.error_non_exist_store_id(store_id)
                else:
                    self.conn.execute(sql, values)
            else:
                self.conn.execute(sql, values)
            book_name = self.conn.fetchall()
            print(book_name)
        except psycopg2.Error as e:
            print(e)
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def whole_content_search(self, sub_content: str, store_id=None):
        try:
            if store_id is None:
                self.conn.execute("select book_id from Book where tscontent @@ to_tsquery('simple',%s);", sub_content)
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
            return 530, "{}".format(str(e))
        print('200')
        return 200, "ok"


# testsearch = Search()
#
# code, message = testsearch.params_search(title='美丽心灵', price=[2000, 5000], store_id='store_1')
# print(code)
