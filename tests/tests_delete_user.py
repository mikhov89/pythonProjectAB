import ast
import json

import pytest

from tests.conftest import send_and_get_response, test_data


class Tests_delete_user:

    # удаление существующего юзера, ждем success
    @pytest.mark.asyncio
    async def test_delete_existing(self, wsf):
        await send_and_get_response(wsf, test_data['create'])
        delete_response = await send_and_get_response(wsf, test_data['delete'])
        assert json.loads(delete_response) == ast.literal_eval(
            f'{{"id": "3", "method": "delete", "status": "success"}}')
        print(json.loads(delete_response))

    # удаление НЕсуществующего юзера, ждем failure
    @pytest.mark.asyncio
    async def test_delete_not_existing(self, wsf):
        delete_response = await send_and_get_response(wsf, test_data['delete'])
        assert json.loads(delete_response) == ast.literal_eval(
            f'{{"id": "3", "method": "delete", "status": "failure"}}')
        print(json.loads(delete_response))

    @pytest.mark.asyncio
    async def test_delete_with_no_phone(self, wsf):
        delete_result = await send_and_get_response(wsf, test_data["delete_no_phone"])
        print(delete_result)
        assert "[json.exception.out_of_range.403] key 'phone' not found" in str(json.loads(delete_result))