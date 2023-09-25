import ast
import json
import pytest

from tests.conftest import send_and_get_response, test_data, check_changes


class TestsWS:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("select_request",
                             [test_data["select_by_name"], test_data["select_by_surname"]])
    async def test_select_by_name_and_surname(self, wsf, select_request):
        await send_and_get_response(wsf, test_data["create"])
        await send_and_get_response(wsf, test_data["create_same_surname_and_name"])
        reply = await send_and_get_response(wsf,
                                            select_request)
        assert json.loads(reply) == ast.literal_eval(
            f'{{\
               "id": "2001",\
               "method": "select",\
               "status": "success",\
               "users": [\
                  {{\
                     "age": 60,\
                     "name": "Harry",\
                     "phone": "2128507",\
                     "surname": "Potter"\
                  }},\
                  {{\
                     "age": 20,\
                     "name": "Harry",\
                     "phone": "2128509",\
                     "surname": "Potter"\
                  }}\
               ]\
              }}')

    @pytest.mark.asyncio
    async def test_select_by_phone(self, wsf):
        await send_and_get_response(wsf, test_data["create"])
        reply = await send_and_get_response(wsf,
                                            test_data["select_by_phone"])
        assert json.loads(reply) == ast.literal_eval(
            f'{{\
               "id": "2000",\
               "method": "select",\
               "status": "success",\
               "users": [\
                  {{\
                     "age": 60,\
                     "name": "Harry",\
                     "phone": "2128507",\
                     "surname": "Potter"\
                  }}\
               ]\
              }}')

    # приводит к сбою приложения
    # @pytest.mark.asyncio
    # async def test_select_with_no_phone(self, wsf):
    #     select_result = await send_and_get_response(wsf, test_data["select_no_data"])
    #     print(select_result)