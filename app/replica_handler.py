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
    while True:
        data = await reader.read(100)
        if not data:
            break
        deserialized_data = deserialize(data)
        if deserialized_data == "PONG":
            # send replconf 1
            writer.write(serialize(["REPLCONF", "listening-port", "6380"]))
        if deserialized_data == "OK":
            # send replconf 2
            writer.write(serialize(["REPLCONF", "capa", "psync2"]))
    await writer.drain()
    writer.close()


async def establish_connection_to_master(MASTER_HOST: str, MASTER_PORT: int):
    reader, writer = await asyncio.open_connection(MASTER_HOST, MASTER_PORT)
    return reader, writer
