import ast
import json

import pytest

from tests.conftest import send_and_get_response, test_data, check_changes


class Tests_update_user:

    # проверяем update - имя, фамилия, возраст, ждем success и проверяем измененные данные
    # тут сразу два бага:
    # 1. Запрос на селект возвращает failure
    # 2. Возраст юзера не обновляется
    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_request",
                             [test_data["update_surname"], test_data["update_name"], test_data["update_age"]])
    async def test_update_existing(self, wsf, update_request, clear_users):
        await send_and_get_response(wsf, test_data["create"])
        repl = await send_and_get_response(wsf, update_request)
        assert json.loads(repl) == ast.literal_eval(
            f'{{"id": "4", "method": "update", "status": "success"}}')
        await check_changes(update_request, wsf)

    @pytest.mark.asyncio
    async def test_update_not_existing(self, wsf, clear_users):
        await send_and_get_response(wsf, f'{{"method": "delete", "id": "10", "phone": "222222"}}')
        repl = await send_and_get_response(wsf,
                                           f'{{"method": "update", "id": "11", "name": "Chuck","surname": "Dorris","phone": "222222","age": 100500}}')
        assert json.loads(repl) == ast.literal_eval(
            f'{{"id": "11", "method": "update", "status": "failure"}}')

    @pytest.mark.asyncio
    async def test_update_with_no_phone(self, wsf, clear_users):
        update_result = await send_and_get_response(wsf, test_data["update_no_phone"])
        assert "[json.exception.out_of_range.403] key " in str(json.loads(update_result))