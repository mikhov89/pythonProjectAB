import ast
import json

import pytest

from tests.conftest import send_and_get_response, test_data, check_changes

class Tests_add_user:

    # создание нового юзера, ждем success
    @pytest.mark.asyncio
    async def test_add_new(self, wsf, clear_users):
        create_response = await send_and_get_response(wsf, test_data['create'])
        assert json.loads(create_response) == ast.literal_eval(
            f'{{"id": "1", "method": "add", "status": "success"}}')
        await check_changes(test_data['create'], wsf)

    # создание существующего юзера, ждем failure
    @pytest.mark.asyncio
    async def test_add_existing(self, wsf, clear_users):
        await send_and_get_response(wsf, test_data['create'])
        create_response_dupl = await send_and_get_response(wsf, test_data['create'])
        assert json.loads(create_response_dupl) == ast.literal_eval(
            f'{{"id": "1", "method": "add", "status": "failure"}}')

    @pytest.mark.asyncio
    @pytest.mark.parametrize("create_request",
                             [test_data["create_no_age"], test_data["create_no_name"], test_data["create_no_surname"],
                              test_data["create_no_phone"]])
    async def test_create_broken(self, wsf, create_request, clear_users):
        dict_create_request = ast.literal_eval(create_request)
        await send_and_get_response(wsf, f'{{"method": "delete", "id": "1003", "phone": "89999999999"}}')
        result = await send_and_get_response(wsf, create_request)
        assert "[json.exception.out_of_range.403] key " in str(json.loads(result))
        select_result = await send_and_get_response(wsf,
                                                    f'{{"id": "2000","method": "select","phone": "89999999999"}}')
        assert (json.loads(select_result)) == {'id': '2000', 'method': 'select', 'status': 'failure'}