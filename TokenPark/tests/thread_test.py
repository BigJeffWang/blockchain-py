# coding:utf-8
import threading
import time


# 方法一：将要执行的方法作为参数传给Thread的构造方法
def action(arg, d):
    time.sleep(1)
    print('the arg is:%s\r' % arg)
    d[str(arg)] = arg


def thread_test():
    d = {}
    thread_list = []
    for i in range(4):
        t = threading.Thread(target=action, args=(i, d))
        t.setDaemon(True)
        thread_list.append(t)
    for t in thread_list:
        t.start()

    for t in thread_list:
        t.join()

    print(d)
    print('main thread end!')

# 方法二：从Thread继承，并重写run()
# class MyThread(threading.Thread):
#     def __init__(self, arg):
#         super(MyThread, self).__init__()  # 注意：一定要显式的调用父类的初始化函数。
#         self.arg = arg
#
#     def run(self):  # 定义每个线程要运行的函数
#         time.sleep(1)
#         print('the arg is:%s\r' % self.arg)
#
#
# for i in range(4):
#     t = MyThread(i)
#     t.start()
#
# print('main thread end!')

if __name__ == "__main__":
    thread_test()
