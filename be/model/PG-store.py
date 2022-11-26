import psycopg2

con = psycopg2.connect(host='dase-cdms-2022.pg.rds.aliyuncs.com', port='5432', user='stu10205501437', password='Stu10205501437', database='stu10205501437')
autocommit = psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
con.set_isolation_level(autocommit)
conn = con.cursor()

sql = 'select current_database();'
# 执行SQL
conn.execute(sql)
# SQL执行后，会将结果以元组的形式缓存在cursor中，使用下述语句输出
for tuple in cur.fetchall():
    print(tuple)

#创建表

conn.execute(
    'CREATE TABLE User1('
    'user_name TEXT PRIMARY KEY,'  # 用户名
    'pwd varchar(15) ,'  # 密码
    'balance INTEGER,'  # 余额
    'token TEXT,'  # token
    'terminal TEXT'  # 端口
    ')'
)

conn.execute(
    'CREATE TABLE IF NOT EXISTS Book( '
    'book_id TEXT PRIMARY KEY,'  # 书本编号
    'title TEXT,'  # 书名
    'author TEXT,'  # 书本信息
    'publisher TEXT,'
    'original_title TEXT,'
    'translator TEXT,'
    'pub_year TEXT,'
    'pages INTEGER,'
    'price INTEGER,'
    'currency_unit TEXT,'
    'binding TEXT,'
    'isbn TEXT,'
    'author_intro TEXT,'
    'book_intro text,'
    'content TEXT,'
    'tags TEXT,'
    'picture BYTEA'
    ')'
)


conn.execute(
    'CREATE TABLE IF NOT EXISTS Store('
    'store_id INTEGER PRIMARY KEY,'  # 店铺编号
    'owner TEXT UNIQUE,'  # 卖家user_name
    'FOREIGN KEY(owner) REFERENCES User1(user_name)'
    ')'
)

conn.execute(
    'CREATE TABLE IF NOT EXISTS Books_in_store( '
    'store_id INTEGER,'  # 店铺编号
    'book_id TEXT,'  # 书本编号
    'book_name TEXT,'  # 书名
    'book_num INTEGER,'  # 在售数量，完成一次订单后数量-1
    'FOREIGN KEY(store_id) REFERENCES Store(store_id),'
    'FOREIGN KEY(book_id) REFERENCES Book(book_id),'
   # 'FOREIGN KEY(book_name) REFERENCES Book(title),'
    'PRIMARY KEY(store_id, book_id)'
    ')'
)

conn.execute(
    'CREATE TABLE IF NOT EXISTS Orders( '
    'order_id INTEGER PRIMARY KEY,'  # 订单编号
    'seller TEXT,'  # 卖家
    'buyer TEXT,'  # 买家
    'status INTEGER,'  # 0为未付款（*这里可以不要 如果我们后面写的是点击购买后直接扣款就直接进入状态1），
    # 1为以付款未发货（买家付款后，商家填入物流前），
    # 2为已发货未收货（商家填入物流后，买家确认收货前），3为已收货完成订单 
    'time TEXT,'  # 下单时间，格式为 'YYYY-MM-DD HH:MM:SS.SSS' 的日期
    'book_id TEXT,'  # 书本编号
    'price INTEGER,'  # 书本价格
    'FOREIGN KEY(seller) REFERENCES Store(owner),'
    'FOREIGN KEY(buyer) REFERENCES User1(user_name),'
    'FOREIGN KEY(book_id) REFERENCES Book(book_id)'
    ')'
)

conn.execute(
    'CREATE TABLE IF NOT EXISTS User_order('
    'user_name TEXT,'  # 用户名
    'order_id INTEGER PRIMARY KEY,'  # 订单号
    'FOREIGN KEY(user_name) REFERENCES User1(user_name),'
    'FOREIGN KEY(order_id) REFERENCES Orders(order_id)'
    ')'
)

conn.execute(
    'CREATE TABLE IF NOT EXISTS User_store('
    'user_name TEXT,'  # 用户名
    'store_id INTEGER PRIMARY KEY,'  # 店铺号
    'FOREIGN KEY(user_name) REFERENCES User1(user_name),'
    'FOREIGN KEY(store_id) REFERENCES Store(store_id)'
    ')'
)

# 插入初始数据

values = [['test_id', 'test_pwd', 100, 'test_token', 'test_terminal'],
          ['test_id_2', 'test_pwd_2', 1000, 'test_token_2', 'test_terminal_2']]
sql = "insert into User1(user_name, pwd, balance, token, terminal) values (%s, %s, %s, %s, %s)"

conn.executemany(sql, values)

values = [['book1', '霸王别姬', '李碧华', '新星出版社', '无', '无', '1', 235, 30, '1', '1', '1', '1', '1', '1', '1']]
sql = "insert into Book(book_id, title, author, publisher, original_title, translator, pub_year , pages, price ," \
      "currency_unit ,binding,isbn ,author_intro,book_intro ,content ,tags) values (%s,%s, %s, %s, %s, %s,%s, %s, %s, " \
      "%s, %s,%s, %s, %s, %s, %s) "

conn.executemany(sql, values)

values = [[1, 'test_id']]
sql = "insert into Store(store_id ,owner) values (%s, %s)"

conn.executemany(sql, values)

values = [[1, 'book1', '霸王别姬', 10]]
sql = "insert into Books_in_store(store_id, book_id, book_name, book_num) values (%s, %s, %s, %s)"

conn.executemany(sql, values)

values = [[1, 'test_id', 'test_id_2', 3, '2022-11-25 23:00:50.000', 'book1', 10]]
sql = "insert into Orders(order_id, seller, buyer, status, time, book_id, price) values (%s, %s, %s, %s, %s, %s, %s)"

conn.executemany(sql, values)

values = [['test_id', 1]]
sql = "insert into User_order(user_name, order_id) values (%s, %s)"

conn.executemany(sql, values)

values = [['test_id', 1]]
sql = "insert into User_store(user_name, store_id) values (%s, %s)"

conn.executemany(sql, values)