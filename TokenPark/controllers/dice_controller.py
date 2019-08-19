from controllers.base_controller import BaseController
from services.dice_service import DiceService
from tools.decorator_tools import FormatOutput


class DiceRecordsController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        start_id = request_data.get("start_id", None)
        user_id = request_data['user_id']
        dice_service = DiceService()
        result = dice_service.dice_records(limit, offset, user_id, start_id)

        return self.utctime_to_localtime(result)


class DiceRecordsGetController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict()
        limit = request_data.get('limit', 10)
        offset = request_data.get('offset', 1)
        start_id = request_data.get("start_id", None)
        dice_service = DiceService()
        result = dice_service.dice_records_get(limit, offset, start_id)

        return self.utctime_to_localtime(result)


class DiceInfoController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['dice_part_id'])
        dice_part_id = request_data['dice_part_id']
        dice_service = DiceService()
        result = dice_service.dice_info(dice_part_id)

        return self.utctime_to_localtime(result)


class DiceChipInController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id', 'coin_id', 'bet_amount', 'user_dice'])
        user_id = request_data['user_id']
        coin_id = request_data['coin_id']
        bet_amount = request_data['bet_amount']
        user_dice = request_data['user_dice']
        user_channel_id = request_data.get("user_channel_id", 0)
        dice_service = DiceService()
        result = dice_service.dice_chip_in_new(user_id, user_channel_id, coin_id, bet_amount, user_dice)
        # result = dice_service.dice_chip_in(user_id, user_channel_id, coin_id, bet_amount, user_dice)

        return self.utctime_to_localtime(result)


class DiceChipInCallbackController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['dice_part_id'])
        dice_id = request_data['dice_part_id']
        dice_service = DiceService()
        result = dice_service.dice_sold_out_new(dice_id)

        return self.utctime_to_localtime(result)


class GetDiceAwardRateController(BaseController):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @FormatOutput()
    def post(self):
        request_data = self.get_argument_dict(must_keys=['user_id'])
        user_id = request_data['user_id']
        dice_service = DiceService()
        result = dice_service.get_dice_award_rate(user_id)

        return self.utctime_to_localtime(result)

