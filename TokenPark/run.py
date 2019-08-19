from api import app
from config import get_bases_conf

if __name__ == '__main__':
    conf = get_bases_conf()["server"]
    app.run(host=conf["host"], port=conf["port"], debug=conf["debug"])
