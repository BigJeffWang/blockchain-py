from models.game_numbers_set_model import GameNumbersSetModel
from services.base_service import BaseService
from tools.mysql_tool import MysqlTools
import random


class GameNumberSetService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def createNumbers(self, dic):
        game_serial = dic.get("game_serial", "")
        total = dic.get("total", 0)
        with MysqlTools().session_scope() as session:
            model = session.query(GameNumbersSetModel).filter(GameNumbersSetModel.game_serial == game_serial).first()
            if model:
                return False

            i = 0
            while total > 0:
                session.add(GameNumbersSetModel(
                    game_serial=game_serial,
                    number=total,
                ))
                i += 1
                if i == 100:
                    session.commit()
                    i = 0

                total -= 1
            session.commit()
            return True

    def getNumbers(self, dic):
        game_serial = dic.get("game_serial", "")
        bet_amount = dic.get("bet_amount", 0)

        with MysqlTools().session_scope() as session:
            models = session.query(GameNumbersSetModel).filter(GameNumbersSetModel.game_serial == game_serial).with_for_update().all()

            numbers = []
            for num in models:
                numbers.append(num.number)

            numbers = random.sample(numbers, bet_amount)
            return numbers

    def deletedNumbers(self, numbers):
        with MysqlTools().session_scope() as session:
            for i in numbers:
                model = session.query(GameNumbersSetModel).filter(
                    GameNumbersSetModel.game_serial == "BTC0011812200001",
                    GameNumbersSetModel.number == i).delete()

            session.commit()
            return model


if __name__ == "__main__":
    # result = GameNumberSetService().createNumbers({"game_serial": "BTC0011812200001", "total": 11})
    # print(result)

    result = GameNumberSetService().getNumbers({"game_serial": "BTC0011812200001", "bet_amount": 4})
    print(result)

    print(GameNumberSetService().deletedNumbers(result))
