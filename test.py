import websockets
import asyncio
import json
import sys
async def do_smth():
    uri = "ws://192.168.64.4:4001"

    async with websockets.connect(uri) as ws:
        await ws.send('{"method": "delete", "id": "2341514214", "phone": "2128507"}')
        repl = await ws.recv()
        print (json.loads(repl))

    async with websockets.connect(uri) as ws:
        await ws.send('{"id": "sfda-11231-123-adfa","method": "add","name": "Chuck","surname": "Dorris","phone": "2128507","age": 100500}')
        repl = await ws.recv()
        print (json.loads(repl))

    async with websockets.connect(uri) as ws:
        await ws.send('{"id": "123412-adf-132111","method": "select","name": "Chuck"}')
        repl = await ws.recv()
        print (json.loads(repl))

    async with websockets.connect(uri) as ws:
        await ws.send('{"id": "sfda-11231-123-adfa","method": "add","name": "Chuck","surname": "Dorris","phone": "2128507","age": 100500}')
        repl = await ws.recv()
        print (json.loads(repl))


asyncio.get_event_loop().run_until_complete(do_smth())