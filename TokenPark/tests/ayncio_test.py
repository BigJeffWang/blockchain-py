import asyncio
import threading
import time


@asyncio.coroutine
def hello(i, d):
    d[str(i)] = i
    if i == 4:
        yield from asyncio.sleep(1)
    print("asyncio " + str(i))


def async_func(arg, loop):
    print("async_func %s" % arg)
    d = {}
    tasks = []
    for i in range(5):
        tasks.append(hello(i, d))
    begin_time = time.time()
    loop.run_until_complete(asyncio.wait(tasks))
    print(time.time() - begin_time)
    print(d)


def work():
    loop = asyncio.get_event_loop()
    for i in range(5):
        async_func(i, loop)
    loop.close()


if __name__ == "__main__":
    work()
