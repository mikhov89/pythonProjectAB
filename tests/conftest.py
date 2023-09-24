import ast
import json

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
             "create_same_req_id":
                 f'{{"id": "11111","method": "add","name": "Harry","surname": "DELETE FROM users WHERE name=\'Harry\';","phone": "Random","age": 30}}',
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
    await wsf.send(f'{{"method": "delete", "id": "1003", "phone": "Random"}}')


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
