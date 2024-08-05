import asyncio
from app.command_handler import command_dispatcher
from app.store import Store
import argparse


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
            to_send, store = command_dispatcher(data, store, server_details)
            writer.write(to_send)
            await writer.drain()
        writer.close()

    server = await asyncio.start_server(handle_client, HOST, PORT)
    async with server:
        await server.serve_forever()
        
if __name__ == "__main__":
    asyncio.run(main())
