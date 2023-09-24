import ast
import json

import pytest
import pytest_asyncio
import websockets

URL = "ws://192.168.64.4:4001"
PHONE = "2128507"
PHONE_2 = "2128508"
PHONE_3 = "2128509"

test_data = {"create":
                 f'{{"id": "1","method": "add","name": "Harry","surname": "Potter","phone": "{PHONE}","age": 60}}',
             "create2":
                 f'{{"id": "2","method": "add","name": "Stiven","surname": "Sigal","phone": "{PHONE_2}","age": 65}}',
             "create_same_surname_and_name":
                 f'{{"id": "2","method": "add","name": "Harry","surname": "Potter","phone": "{PHONE_3}","age": 20}}',
             "create_no_age":
                 f'{{"id": "2","method": "add","name": "Harry","surname": "Potter","phone": "89999999999"}}',
             "create_no_name":
                 f'{{"id": "2","method": "add","surname": "Potter","phone": "89999999999", "age": 20}}',
             "create_no_surname":
                 f'{{"id": "2","method": "add","name": "Harry","phone": "89999999999","age": 20}}',
             "create_no_phone":
                 f'{{"id": "2","method": "add","name": "Harry","surname": "Potter","age": 20}}',
             "create_wrong_req_id":
                 f'{{"id": "!jkfsgjfldsdfldajk$#","method": "add","name": "Harry","surname": "Potter","phone": "89999999999","age": 20}}',
             "delete": f'{{"method": "delete", "id": "3", "phone": "{PHONE}"}}',
             "delete_no_phone": f'{{"method": "delete", "id": "3"}}',
             "update_surname":
                 f'{{"method": "update", "id": "4", "name": "Chuck","surname": "NEW_Dorris","phone": "{PHONE}","age": 60}}',
             "update_name":
                 f'{{"method": "update", "id": "4", "name": "NEW_Chuck","surname": "Dorris","phone": "{PHONE}","age": 60}}',
             "update_age":
                 f'{{"method": "update", "id": "4", "name": "Harry","surname": "Dorris","phone": "{PHONE}","age": 65}}',
             "update_phone":
                 f'{{"method": "update", "id": "4", "name": "Harry","surname": "Dorris","phone": "{PHONE_2}","age": 60}}',
             "update_no_phone":
                 f'{{"method": "update", "id": "4", "name": "Harry","surname": "Dorris","age": 60}}',
             "select_by_phone": f'{{"id": "2000","method": "select","phone": "{PHONE}"}}',
             "select_by_name": f'{{"id": "2001","method": "select","name": "Harry"}}',
             "select_by_surname": f'{{"id": "2001","method": "select","surname": "Potter"}}',
             "select_no_data": f'{{"id": "2002","method": "select"}}',
             }


@pytest_asyncio.fixture()
async def wsf():
    async with websockets.connect(URL) as socket:
        yield socket


@pytest_asyncio.fixture(autouse=True)
async def clear_users(wsf):
    yield
    await wsf.send(f'{{"method": "delete", "id": "1000", "phone": "{PHONE}"}}')
    await wsf.send(f'{{"method": "delete", "id": "1001", "phone": "{PHONE_2}"}}')
    await wsf.send(f'{{"method": "delete", "id": "1002", "phone": "{PHONE_3}"}}')
    await wsf.send(f'{{"method": "delete", "id": "1003", "phone": "89999999999"}}')


async def send_and_get_response(ws, request):
    await ws.send(request)
    return await ws.recv()


async def check_changes(expected, socket):
    dict_view = ast.literal_eval(expected)
    new_data = await send_and_get_response(socket,
                                           f'{{"id": "{dict_view["id"]}","method": "select","phone": "{dict_view["phone"]}"}}')
    assert json.loads(new_data) == ast.literal_eval(
        f'{{\
       "id": "{dict_view["id"]}",\
       "method": "select",\
       "status": "success",\
       "users": [\
         {{\
           "age":{dict_view["age"]},\
           "name": "{dict_view["name"]}",\
           "phone": "{dict_view["phone"]}",\
           "surname": "{dict_view["surname"]}"\
         }}\
       ]\
     }}')


class TestsWS:

    # создание нового юзера, ждем success
    @pytest.mark.asyncio
    async def test_add_new(self, wsf):
        create_response = await send_and_get_response(wsf, test_data['create'])
        assert json.loads(create_response) == ast.literal_eval(
            f'{{"id": "1", "method": "add", "status": "success"}}')
        print(json.loads(create_response))
        await check_changes(test_data['create'], wsf)

    # создание существующего юзера, ждем failure
    @pytest.mark.asyncio
    async def test_add_existing(self, wsf):
        await send_and_get_response(wsf, test_data['create'])
        create_response_dupl = await send_and_get_response(wsf, test_data['create'])
        assert json.loads(create_response_dupl) == ast.literal_eval(
            f'{{"id": "1", "method": "add", "status": "failure"}}')
        print(json.loads(create_response_dupl))

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

    # проверяем update - имя, фамилия, возраст, ждем success и проверяем измененные данные
    # тут сразу два бага:
    # 1. Запрос на селект возвращает failure
    # 2. Возраст юзера не обновляется
    @pytest.mark.asyncio
    @pytest.mark.parametrize("update_request",
                             [test_data["update_surname"], test_data["update_name"], test_data["update_age"]])
    async def test_update_existing(self, wsf, update_request):
        await send_and_get_response(wsf, test_data["create"])
        repl = await send_and_get_response(wsf, update_request)
        assert json.loads(repl) == ast.literal_eval(
            f'{{"id": "4", "method": "update", "status": "success"}}')
        await check_changes(update_request, wsf)

    @pytest.mark.asyncio
    async def test_update_not_existing(self, wsf):
        await send_and_get_response(wsf, f'{{"method": "delete", "id": "10", "phone": "222222"}}')
        repl = await send_and_get_response(wsf,
                                           f'{{"method": "update", "id": "11", "name": "Chuck","surname": "Dorris","phone": "222222","age": 100500}}')
        assert json.loads(repl) == ast.literal_eval(
            f'{{"id": "11", "method": "update", "status": "failure"}}')
        print(json.loads(repl))

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
    @pytest.mark.parametrize("create_request",
                             [test_data["create_no_age"], test_data["create_no_name"], test_data["create_no_surname"],
                              test_data["create_no_phone"]])
    async def test_create_broken(self, wsf, create_request):
        dict_create_request = ast.literal_eval(create_request)
        await send_and_get_response(wsf, f'{{"method": "delete", "id": "1003", "phone": "89999999999"}}')
        result = await send_and_get_response(wsf, create_request)
        assert "[json.exception.out_of_range.403] key " in str(json.loads(result))
        select_result = await send_and_get_response(wsf,
                                                    f'{{"id": "2000","method": "select","phone": "89999999999"}}')
        assert (json.loads(select_result)) == {'id': '2000', 'method': 'select', 'status': 'failure'}

    # приводит к сбою приложения
    # @pytest.mark.asyncio
    # async def test_select_with_no_phone(self, wsf):
    #     select_result = await send_and_get_response(wsf, test_data["select_no_data"])
    #     print(select_result)

    @pytest.mark.asyncio
    async def test_delete_with_no_phone(self, wsf):
        delete_result = await send_and_get_response(wsf, test_data["delete_no_phone"])
        print(select_result)
        assert "[json.exception.out_of_range.403] key " in str(json.loads(delete_result))

    @pytest.mark.asyncio
    async def test_update_with_no_phone(self, wsf):
        update_result = await send_and_get_response(wsf, test_data["update_no_phone"])
        print(update_result)
        assert "[json.exception.out_of_range.403] key " in str(json.loads(update_result))