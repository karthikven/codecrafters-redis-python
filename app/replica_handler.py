import asyncio
import argparse
from app.resp import serialize, deserialize

async def handle_replica(REPLICAOF: str):
    replica_split = REPLICAOF.split(" ")
    master_host, master_port = replica_split[0], int(replica_split[1])

    reader, writer = await establish_connection_to_master(master_host, master_port)
    await handshake_with_master(reader, writer)
    

async def handshake_with_master(reader, writer):
    # send ping
    writer.write(serialize(["PING"]))
    response_arr = []

    while True:
        data = await reader.read(100)
        if not data:
            break
        print("IN HANDSHAKE WITH MASTER: ", data)
        if len(data) <= 10:
            deserialized_data = deserialize(data)
            if len(response_arr) == 0 and deserialized_data == "PONG":
                # send replconf 1
                response_arr.append(deserialized_data)
                writer.write(serialize(["REPLCONF", "listening-port", "6380"]))
                deserialized_data = ""
            if len(response_arr) == 1 and deserialized_data == "OK":
                # send replconf 2
                response_arr.append(deserialized_data)
                writer.write(serialize(["REPLCONF", "capa", "psync2"]))
                deserialized_data = ""
            if len(response_arr) == 2 and deserialized_data == "OK":
                response_arr.append(deserialized_data)
                writer.write(serialize(["PSYNC", "?", "-1"]))
                deserialized_data = ""

    await writer.drain()
    writer.close()


async def establish_connection_to_master(MASTER_HOST: str, MASTER_PORT: int):
    reader, writer = await asyncio.open_connection(MASTER_HOST, MASTER_PORT)
    return reader, writer
