from be.model.order_list import Order
import time
import datetime


time_limit = 900
unpaid_orders = {}


def get_time_stamp():
    cur_time_stamp = time.time()
    return int(cur_time_stamp)


def unpaid_order(order_id):
    unpaid_orders[order_id] = get_time_stamp()
    return 200, "ok"


def remove_overtime_order(order_id):
    try:
        unpaid_orders.pop(order_id)
    except BaseException as e:
        return 530, "{}".format(str(e))
    return 200, "ok"


def check_order_time(order_time):
    cur_time = time.time()
    st_ti = time.strptime(order_time,'%Y-%m-%d %H:%M:%S')
    print("----------------st_ti:", st_ti)
    order_time = time.mktime(st_ti)
    time_diff = (cur_time - order_time)
    if time_diff > time_limit:
        return False
    else:
        return True


def auto_delete():
    temp = []
    order = Order()
    for (oid, tim) in unpaid_orders.items():
        if check_order_time(tim) == False:
            temp.append(oid)
    for oid in temp:
        remove_overtime_order(oid)
        order.cancel_order(oid)
    return 0