import asyncio
import argparse
from app.resp import serialize

async def handle_replica(REPLICAOF: str):
    replica_split = REPLICAOF.split(" ")
    master_host, master_port = replica_split[0], int(replica_split[1])
    reader, writer = await establish_connection_to_master(master_host, master_port)
    writer.write(serialize(["PING"]))
    await writer.drain()
    writer.close()

async def establish_connection_to_master(MASTER_HOST: str, MASTER_PORT: int):
    reader, writer = await asyncio.open_connection(MASTER_HOST, MASTER_PORT)
    return reader, writer
