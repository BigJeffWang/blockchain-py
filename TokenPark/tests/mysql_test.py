from tools.mysql_tool import MysqlTools
from models.token_conf_model import TokenConfModel
import asyncio
import threading


@asyncio.coroutine
def hello():
    print("2.1 befor yield from asyncio sleep")
    r = yield from asyncio.sleep(2)
    print("2.1 after yield from asyncio sleep")


def hello2():
    print("2.2 befor yield from asyncio sleep")
    r = yield from asyncio.sleep(5)
    print("2.2 after yield from asyncio sleep")


@asyncio.coroutine
def test_mysql():
    with MysqlTools().session_scope() as session:
        yield from asyncio.sleep(10)
        res = session.query(TokenConfModel).first()
        print(res.coid)


loop = asyncio.get_event_loop()
print("1. after get event loop")

# loop.run_until_complete(hello())

# tasks = [hello2(), hello()]
# tasks = [hello2()]
# for i in range(5):
#     tasks.append(hello())
tasks = []
for i in range(100):
    tasks.append(test_mysql())

loop.run_until_complete(asyncio.wait(tasks))

print("2. after run")

loop.close()
print("3. after close")
