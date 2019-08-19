from utils.log import TimingLog


def test():
    TimingLog.begin()
    TimingLog.end()


def test2():
    test()


def test3():
    test2()


if __name__ == "__main__":
    test3()
    a = 3
    print(a.hasattr("name"))
