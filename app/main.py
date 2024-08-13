import asyncio
from app.command_handler import command_dispatcher
from app.store import Store
import argparse
from app.replica_handler import handle_replica
import base64


async def main():
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=6379)
    parser.add_argument('--replicaof', type=str)
    args = parser.parse_args()

    HOST = "localhost"
    PORT = args.port
    REPLICAOF = args.replicaof
    master_replid = "8371b4fb1155b71f4a04d3e1bc3e18c4a990aeeb"
    master_repl_offset = 0
    replicas_to_propagate_to = set()

    if REPLICAOF:
        await handle_replica(REPLICAOF)

    async def handle_client(reader, writer):
        store = Store()
        server_details = {
            "REPLICAOF": REPLICAOF,
            "master_replid": master_replid,
            "master_repl_offset": master_repl_offset
        }
        while True:
            data = await reader.read(100)
            if not data:
                break
            to_send, store, rdb_flag, to_propagate = command_dispatcher(data, store, server_details)
            if rdb_flag:
                writer.write(to_send)
                BULK_STRING = b'$'
                CRLF = b'\r\n'
                empty_rdb_in_base64 = "UkVESVMwMDEx+glyZWRpcy12ZXIFNy4yLjD6CnJlZGlzLWJpdHPAQPoFY3RpbWXCbQi8ZfoIdXNlZC1tZW3CsMQQAPoIYW9mLWJhc2XAAP/wbjv+wP9aog=="
                binary_rdb = base64.b64decode(empty_rdb_in_base64)
                len_binary_rdb = str(len(binary_rdb)).encode('utf-8')
                rdb_to_send =  BULK_STRING + len_binary_rdb + CRLF + binary_rdb
                writer.write(rdb_to_send)
                replicas_to_propagate_to.add(writer)
            else:
                writer.write(to_send)
                if to_propagate:
                    for replica_writer in replicas_to_propagate_to:
                        replica_writer.write(data)
                        await replica_writer.drain()
            await writer.drain()
        writer.close()

    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
