from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from typing import List
import asyncio
from aiokafka import AIOKafkaProducer
from .schemas import ProducerMessage
from .schemas import ProducerResponse
from .schemas import RuleSetBook, Inventory, Activation, ActivationLog, Extravars
from .models import metadata, rulesets, inventories, extravars, activations
from .manager import activate_rulesets
import json

import databases
import sqlalchemy
from sqlalchemy import select
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"

database = databases.Database(DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


app = FastAPI()


loop = asyncio.get_event_loop()
aioproducer = AIOKafkaProducer(loop=loop, bootstrap_servers="localhost:9092")


@app.on_event("startup")
async def startup():
    await aioproducer.start()
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    await aioproducer.stop()


@app.get("/")
async def root():
    return {"message": "Hello World"}


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@app.get("/demo")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


@app.get("/ping")
def ping():
    return {"ping": "pong!"}


@app.post("/producer/{topicname}")
async def kafka_produce(msg: ProducerMessage, topicname: str):
    """
    Produce a message into <topicname>
    This will produce a message into a Apache Kafka topic
    And this path operation will:
    * return ProducerResponse
    """

    await aioproducer.send(topicname, json.dumps(msg.dict()).encode("ascii"))
    response = ProducerResponse(
        name=msg.name, message_id=msg.message_id, topic=topicname
    )
    return response


@app.post("/rulesetbook/")
async def create_rulesetbook(rsb: RuleSetBook):
    query = rulesets.insert().values(name=rsb.name, rules=rsb.rules)
    last_record_id = await database.execute(query)
    return {**rsb.dict(), "id": last_record_id}


@app.post("/inventory/")
async def create_inventory(i: Inventory):
    query = inventories.insert().values(name=i.name, inventory=i.inventory)
    last_record_id = await database.execute(query)
    return {**i.dict(), "id": last_record_id}


@app.post("/extravars/")
async def create_extravars(e: Extravars):
    query = extravars.insert().values(name=e.name, extravars=e.extravars)
    last_record_id = await database.execute(query)
    return {**e.dict(), "id": last_record_id}


@app.post("/activation/")
async def create_activation(a: Activation):
    query = rulesets.select().where(rulesets.c.id==a.rulesetbook_id)
    r = await database.fetch_one(query)
    query = inventories.select().where(inventories.c.id==a.inventory_id)
    i = await database.fetch_one(query)
    query = extravars.select().where(extravars.c.id==a.extravars_id)
    e = await database.fetch_one(query)
    await activate_rulesets(
        "quay.io/bthomass/events-demo-ci-cd:latest",
        r.rules,
        i.inventory,
        e.extravars
    )

    query = activations.insert().values(
        name=a.name,
        rulesetbook_id=a.rulesetbook_id,
        inventory_id=a.inventory_id,
        extravars_id=a.extravars_id,
    )
    last_record_id = await database.execute(query)
    return {**a.dict(), "id": last_record_id}


@app.post("/activationlog/")
async def create_activation_log(al: ActivationLog):
    return {**al.dict(), "id": last_record_id}
