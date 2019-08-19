from services.base_service import BaseService
from utils.bet_number_util import get_bet_number
from utils.log import Slog


class TestqwerServie(object):
    slog = Slog("test4")

    def test4(self):
        self.slog.info("dasdada121d1dd1")


if __name__ == "__main__":
    TestqwerServie().test4()
