from api import app
from config import get_conf
base = get_conf("bases")


if __name__ == '__main__':
    app.run(host=base["server_host"], port=base["server_port"], debug=True)