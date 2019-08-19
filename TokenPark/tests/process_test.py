from multiprocessing import Process, Value
import time


class MyProcess(Process):
    alive = Value('b', True)

    def __init__(self, name, d):
        super(MyProcess, self).__init__()
        self.d = d
        self.d[name] = name

    def run(self):
        time.sleep(10)
        # while True:
        #     if self.alive.value:
        #         time.sleep(0.1)
        #         print("running..." + str(time.time()))
        #     else:
        #         break

    def terminating(self):
        print("terminate")
        self.alive.value = False


if __name__ == '__main__':
    dd = {}
    for i in range(10):
        p = MyProcess(str(i), dd)
        p.start()  # 就是调用run()方法。
        print("main=======")
        # p.terminating()
    print(dd)
